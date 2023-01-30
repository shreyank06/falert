from uuid import UUID
from typing import List, Optional, Tuple
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import select
from shapely.geometry import Point, Polygon

from falert.backend.common.input import TriggerMatchingInputSchema
from falert.backend.common.output import (
    TriggerNotifyingOutput,
    TriggerNotifyingOutputSchema,
)
from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.messenger import AsyncpgReceiver, AsyncpgSender
from falert.backend.common.entity import (
    SubscriptionEntity,
    SubscriptionMatchEntity,
    SubscriptionMatchFireLocationEntity,
    FireLocationEntity,
)


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        self.__receiver = None
        self.__sender = None

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            self.__receiver = AsyncpgReceiver(
                raw_connection.dbapi_connection.driver_connection
            )

            self.__sender = AsyncpgSender(
                raw_connection.dbapi_connection.driver_connection
            )

            await self.__handle_matching(None, None)

            while True:
                trigger_matching_input = TriggerMatchingInputSchema().loads(
                    await self.__receiver.receive("trigger_matching")
                )

                await self.__handle_matching(
                    trigger_matching_input.subscription_ids,
                    trigger_matching_input.dataset_harvest_ids,
                )

    # pylint: disable=too-many-locals
    async def __handle_matching(
        self,
        subscription_ids: Optional[List[UUID]],
        dataset_harvest_ids: Optional[List[UUID]],
    ) -> None:
        self._logger.info("Start matching")

        session_maker = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        fire_location_entities = []
        subscription_entities = []

        async with session_maker() as database_session:
            if dataset_harvest_ids is None or len(dataset_harvest_ids) == 0:
                self._logger.info("Fetch fire locations from the last 24 hours")

                fire_location_entities = list(
                    await database_session.execute(
                        select(FireLocationEntity).where(
                            FireLocationEntity.created
                            >= datetime.utcnow() - timedelta(hours=24)
                        )
                    )
                )
            else:
                self._logger.info(
                    "Fetch all fire locations from dataset harvests with ids %s",
                    ", ".join(map(str, dataset_harvest_ids)),
                )

                fire_location_entities = list(
                    await database_session.execute(
                        select(FireLocationEntity).where(
                            FireLocationEntity.dataset_harvest_id.in_(
                                dataset_harvest_ids
                            )
                        )
                    )
                )

            if subscription_ids is None or len(subscription_ids) == 0:
                self._logger.info("Fetch all subscriptions")

                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .options(
                                joinedload(SubscriptionEntity.subscription_vertices)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_matches
                                ).joinedload(
                                    SubscriptionMatchEntity.subscription_match_fire_locations
                                )
                            )
                        )
                    ).unique()
                )
            else:
                self._logger.info(
                    "Fetch all subscriptions with ids %s",
                    ", ".join(map(str, subscription_ids)),
                )

                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .where(SubscriptionEntity.id.in_(subscription_ids))
                            .options(
                                joinedload(SubscriptionEntity.subscription_vertices)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_matches
                                ).joinedload(
                                    SubscriptionMatchEntity.subscription_match_fire_locations
                                )
                            )
                        )
                    ).unique()
                )

        self._logger.info(
            "Match %s subscription(s) with %s fire location(s)",
            len(subscription_entities),
            len(fire_location_entities),
        )

        subscription_match_ids = []

        for (subscription_entity,) in subscription_entities:
            async with session_maker() as database_session:
                polygon = Polygon(
                    map(
                        lambda x: (x.latitude, x.longitude),
                        subscription_entity.subscription_vertices,
                    )
                )

                subscription_entity_matches_fire_locations = set()

                for (
                    subscription_match_entity
                ) in subscription_entity.subscription_matches:
                    for (
                        subscription_match_fire_location_entity
                    ) in subscription_match_entity.subscription_match_fire_locations:
                        subscription_entity_matches_fire_locations.add(
                            subscription_match_fire_location_entity.fire_location_id
                        )

                subscription_match_entity = SubscriptionMatchEntity()
                subscription_entity.subscription_matches.append(
                    subscription_match_entity
                )

                for (fire_location_entity,) in fire_location_entities:
                    fire_location_point = Point(
                        fire_location_entity.latitude,
                        fire_location_entity.longitude,
                    )

                    if (
                        fire_location_entity.id
                        not in subscription_entity_matches_fire_locations
                        and polygon.contains(fire_location_point)
                    ):
                        subscription_match_entity.subscription_match_fire_locations.append(
                            SubscriptionMatchFireLocationEntity(
                                fire_location_id=fire_location_entity.id
                            )
                        )

                if len(subscription_match_entity.subscription_match_fire_locations) > 0:
                    self._logger.info(
                        "Subscription %s has a match with %s new fire location(s)",
                        subscription_entity.id,
                        len(
                            subscription_match_entity.subscription_match_fire_locations
                        ),
                    )

                    database_session.add(subscription_entity)
                    await database_session.commit()

                    subscription_match_ids.append(
                        subscription_match_entity.id,
                    )

        if len(subscription_match_ids) > 0:
            trigger_notifying_output = TriggerNotifyingOutput(
                subscription_match_ids,
            )

            await self.__sender.send(
                "trigger_notifying",
                TriggerNotifyingOutputSchema().dumps(
                    trigger_notifying_output,
                ),
            )

        self._logger.info("Finish matching")
