from asyncio import get_running_loop
from base64 import b64decode, b64encode

from asyncpg import Connection


class Sender:
    async def send(self, channel_name: str, data: str) -> None:
        await self._on_send(channel_name, b64encode(data.encode()).decode())

    async def _on_send(self, channel_name: str, data: str) -> None:
        raise NotImplementedError()


class Receiver:
    async def receive(self, channel_name: str) -> str:
        data = await self._on_receive(channel_name)
        return b64decode(data).decode()

    async def _on_receive(self, channel_name: str) -> str:
        raise NotImplementedError()


class AsyncpgSender(Sender):
    def __init__(self, connection: Connection) -> None:
        super().__init__()

        self.__connection = connection

    async def _on_send(self, channel_name: str, data: str) -> None:
        await self.__connection.execute(f"NOTIFY {channel_name}, '{data}';")


class AsyncpgReceiver(Receiver):
    def __init__(self, connection: Connection) -> None:
        super().__init__()

        self.__connection = connection

    async def _on_receive(self, channel_name: str) -> str:
        loop = get_running_loop()
        future = loop.create_future()
        listener = lambda connection, channel_name, pid, data: future.set_result(data)

        await self.__connection.add_listener(channel_name, listener)
        data = await future
        await self.__connection.remove_listener(channel_name, listener)

        return data
