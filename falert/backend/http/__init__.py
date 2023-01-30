from sanic import Sanic
from sanic.response import HTTPResponse
from sanic_ext import Extend

from falert.backend.common.messenger import AsyncpgSender
from falert.backend.common.application import BaseApplication
from falert.backend.http.view import (
    PingView,
    SubscriptionCreateView,
    StatisticsReadView,
)
from falert.backend.http.middleware import (
    AttachDatabaseMiddleware,
    DetachDatabaseMiddleware,
    AttachSenderMiddleware,
)
from falert.backend.common.entity import BaseEntity


class Application(BaseApplication):
    @staticmethod
    def run():
        Application().main()

    async def __before_server_start(self, *_args, **_kwargs):
        async with self._engine.begin() as connection:
            await connection.run_sync(BaseEntity.metadata.create_all)

            raw_connection = await connection.get_raw_connection()

            # pylint: disable=unused-private-member
            self.__sender = AsyncpgSender(
                raw_connection.dbapi_connection.driver_connection
            )

            self.__sanic.register_middleware(
                AttachSenderMiddleware(self.__sender),
                "request",
            )

    def __init__(self) -> None:
        super().__init__()

        self.__sender = None

        self.__sanic = Sanic(
            name="falert-backend-http",
        )

        self.__sanic.config.CORS_ORIGINS = "*"
        self.__sanic.config.CORS_SEND_WILDCARD = True
        Extend(self.__sanic)

        self.__sanic.register_middleware(
            AttachDatabaseMiddleware(self._engine),
            "request",
        )

        self.__sanic.register_middleware(
            DetachDatabaseMiddleware(),
            "response",
        )

        self.__sanic.register_listener(
            self.__before_server_start,
            "before_server_start",
        )

        self.__sanic.add_route(PingView.as_view(), "/ping")
        self.__sanic.add_route(SubscriptionCreateView.as_view(), "/subscriptions")
        self.__sanic.add_route(StatisticsReadView.as_view(), "/statistics")

        self.__sanic.static("/", "./build/index.html")
        self.__sanic.static("/_app", "./build/_app")
        self.__sanic.static("/favicon.png", "./build/favicon.png")

    def main(self):
        print(self._configuration.http_port)
        self.__sanic.run(port=self._configuration.http_port)
