from asyncio import run
from logging import Logger, getLogger, DEBUG, basicConfig

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from falert.backend.common.configuration import Configuration, load_from_environment


class BaseApplication:
    def __init__(self):
        self.__configuration = load_from_environment()

        self.__engine = create_async_engine(
            self.__configuration.database_url,
            echo=self.__configuration.database_echo,
        )

        self.__logger = getLogger(None)
        basicConfig()
        self.__logger.setLevel(DEBUG)

    @property
    def _configuration(self) -> Configuration:
        return self.__configuration

    @property
    def _engine(self) -> AsyncEngine:
        return self.__engine

    @property
    def _logger(self) -> Logger:
        return self.__logger


class AsynchronousApplication(BaseApplication):
    @classmethod
    def run(cls):
        run(cls().main())

    async def main(self):
        raise NotImplementedError()
