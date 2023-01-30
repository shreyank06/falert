from csv import DictReader
from logging import Logger
from asyncio import gather
from tempfile import NamedTemporaryFile

from aiohttp import ClientSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.output import (
    TriggerMatchingOutput,
    TriggerMatchingOutputSchema,
)
from falert.backend.common.entity import (
    BaseEntity,
    DatasetEntity,
    FireLocationEntity,
    DatasetHarvestEntity,
)
from falert.backend.common.input import NASAFireLocationInputSchema
from falert.backend.common.messenger import AsyncpgSender, Sender


class BaseHarvester:
    pass


class NASAHarvester(BaseHarvester):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        engine: AsyncEngine,
        sender: Sender,
        logger: Logger,
        url: str,
        chunk_size: int = 8192,
    ):
        super().__init__()

        self.__engine = engine
        self.__sender = sender
        self.__logger = logger
        self.__url = url
        self.__chunk_size = chunk_size

    # pylint: disable=too-many-locals
    async def run(self):
        session_maker = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with session_maker() as database_session:
            result = await database_session.execute(
                select(DatasetEntity)
                .options(
                    joinedload(DatasetEntity.dataset_harvests).joinedload(
                        DatasetHarvestEntity.fire_locations
                    )
                )
                .where(DatasetEntity.url == self.__url)
            )

            dataset_entity = list(result.unique())
            reported_fire_locations = {}

            if dataset_entity is None or len(dataset_entity) == 0:
                self.__logger.info("Create new dataset")
                dataset_entity = DatasetEntity(url=self.__url)
            else:
                dataset_entity = dataset_entity[0][0]

                for dataset_harvest_entity in dataset_entity.dataset_harvests:
                    for fire_location in dataset_harvest_entity.fire_locations:
                        reported_fire_locations[
                            (
                                fire_location.latitude,
                                fire_location.longitude,
                                fire_location.acquired,
                            )
                        ] = fire_location

                self.__logger.info(
                    # pylint: disable=line-too-long
                    f"Update dataset {dataset_entity.id} with {len(reported_fire_locations)} fire locations"
                )

            dataset_harvest_entity = DatasetHarvestEntity()

            async with ClientSession() as client_session:
                self.__logger.info(
                    f"Download {self.__url} for dataset {dataset_entity.id}"
                )

                async with client_session.get(self.__url) as response:
                    with NamedTemporaryFile() as write_file:
                        self.__logger.info(f"Save response for url {self.__url}")

                        async for data in response.content.iter_chunked(
                            self.__chunk_size
                        ):
                            write_file.write(data)

                        write_file.flush()

                        self.__logger.info(f"Read CSV data for url {self.__url}")

                        with open(write_file.name, "r", encoding="utf-8") as read_file:
                            reader = DictReader(read_file)

                            for row in reader:
                                fire_location_input = (
                                    NASAFireLocationInputSchema().load(row)
                                )

                                if (
                                    fire_location_input.latitude,
                                    fire_location_input.longitude,
                                    fire_location_input.acquired,
                                ) not in reported_fire_locations:
                                    dataset_harvest_entity.fire_locations.append(
                                        FireLocationEntity(
                                            latitude=fire_location_input.latitude,
                                            longitude=fire_location_input.longitude,
                                            raw=row,
                                            acquired=fire_location_input.acquired,
                                        )
                                    )

            self.__logger.info(
                # pylint: disable=line-too-long
                f"Add {len(dataset_harvest_entity.fire_locations)} new fire locations to dataset {dataset_entity.id}"
            )

            dataset_entity.dataset_harvests.append(dataset_harvest_entity)
            database_session.add(dataset_entity)
            await database_session.commit()

            trigger_matching_output = TriggerMatchingOutput(
                dataset_harvest_ids=[
                    dataset_harvest_entity.id,
                ],
            )

            await self.__sender.send(
                "trigger_matching",
                TriggerMatchingOutputSchema().dumps(
                    trigger_matching_output,
                ),
            )


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        self.__sender = None

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            self.__sender = AsyncpgSender(
                raw_connection.dbapi_connection.driver_connection
            )

        harvester0 = NASAHarvester(
            self._engine,
            self.__sender,
            self._logger,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv",
        )

        harvester1 = NASAHarvester(
            self._engine,
            self.__sender,
            self._logger,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
        )

        harvester2 = NASAHarvester(
            self._engine,
            self.__sender,
            self._logger,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv",
        )

        await gather(
            harvester0.run(),
            harvester1.run(),
            harvester2.run(),
        )
