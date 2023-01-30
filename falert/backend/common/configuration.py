from typing import Mapping, Any
from os import getenv

from marshmallow import Schema, post_load
from marshmallow.fields import String, Boolean, Int
from dotenv import load_dotenv


class Configuration:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        database_url: str,
        database_echo: bool,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region_name: str,
        dry: bool,
        http_port: int,
    ) -> None:
        self.__database_url = database_url
        self.__database_echo = database_echo
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__aws_region_name = aws_region_name
        self.__dry = dry
        self.__http_port = http_port

    @property
    def database_url(self) -> str:
        return self.__database_url

    @property
    def database_echo(self) -> bool:
        return self.__database_echo

    @property
    def aws_access_key_id(self) -> str:
        return self.__aws_access_key_id

    @property
    def aws_secret_access_key(self) -> str:
        return self.__aws_secret_access_key

    @property
    def aws_region_name(self) -> str:
        return self.__aws_region_name

    @property
    def dry(self) -> bool:
        return self.__dry

    @property
    def http_port(self) -> int:
        return self.__http_port


class ConfigurationSchema(Schema):
    database_url = String(required=True)
    database_echo = Boolean(allow_none=True, load_default=False)
    aws_access_key_id = String(required=True)
    aws_secret_access_key = String(required=True)
    aws_region_name = String(required=True)
    dry = Boolean(allow_none=True, load_default=True)
    http_port = Int(allow_none=True, load_default=8080)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(self, values: Mapping[str, Any], **_kwargs) -> Configuration:
        return Configuration(**values)


def load_from_environment() -> Configuration:
    load_dotenv()

    return ConfigurationSchema().load(
        dict(
            map(
                lambda key: (key, getenv(key.upper())),
                vars(ConfigurationSchema)["_declared_fields"].keys(),
            )
        )
    )
