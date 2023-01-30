from uuid import UUID
from typing import List, Any, Optional, Mapping
from datetime import datetime

from marshmallow import Schema, fields, post_load


class BaseInput:
    pass


class SubscriptionVertexInput(BaseInput):
    def __init__(self, longitude: float, latitude: float) -> None:
        super().__init__()

        self.__longitude = longitude
        self.__latitude = latitude

    @property
    def longitude(self) -> float:
        return self.__longitude

    @property
    def latitude(self) -> float:
        return self.__latitude


class SubscriptionVertexInputSchema(Schema):
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> SubscriptionVertexInput:
        return SubscriptionVertexInput(**values)


class SubscriptionInput(BaseInput):
    def __init__(
        self, phone_number: str, vertices: List["SubscriptionVertexInput"]
    ) -> None:
        super().__init__()

        self.__phone_number = phone_number
        self.__vertices = vertices

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def vertices(self) -> List["SubscriptionVertexInput"]:
        return self.__vertices


class SubscriptionInputSchema(Schema):
    phone_number = fields.String(required=True)
    vertices = fields.List(fields.Nested(SubscriptionVertexInputSchema, required=True))

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(self, values: Mapping[str, Any], **_kwargs) -> SubscriptionInput:
        return SubscriptionInput(**values)


# pylint: disable=too-many-instance-attributes
class NASAFireLocationInput(BaseInput):
    # pylint: disable=too-many-arguments, too-many-locals
    def __init__(
        self,
        latitude: float,
        longitude: float,
        scan: float,
        track: float,
        acq_date: str,
        acq_time: str,
        satellite: str,
        confidence: Any,
        version: str,
        frp: float,
        daynight: str,
        brightness: Optional[float] = None,
        bright_t31: Optional[float] = None,
        bright_ti4: Optional[float] = None,
        bright_ti5: Optional[float] = None,
    ) -> None:
        super().__init__()

        self.__latitude = latitude
        self.__longitude = longitude
        self.__brightness = brightness
        self.__scan = scan
        self.__track = track
        self.__acq_date = acq_date
        self.__acq_time = acq_time
        self.__satellite = satellite
        self.__confidence = confidence
        self.__version = version
        self.__frp = frp
        self.__daynight = daynight
        self.__bright_t31 = bright_t31
        self.__bright_ti4 = bright_ti4
        self.__bright_ti5 = bright_ti5

    @property
    def latitude(self) -> float:
        return self.__latitude

    @property
    def longitude(self) -> float:
        return self.__longitude

    @property
    def brightness(self) -> Optional[float]:
        return self.__brightness

    @property
    def scan(self) -> float:
        return self.__scan

    @property
    def track(self) -> float:
        return self.__track

    @property
    def acq_date(self) -> str:
        return self.__acq_date

    @property
    def acq_time(self) -> str:
        return self.__acq_time

    @property
    def satellite(self) -> str:
        return self.__satellite

    @property
    def confidence(self) -> Any:
        return self.__confidence

    @property
    def version(self) -> str:
        return self.__version

    @property
    def frp(self) -> float:
        return self.__frp

    @property
    def daynight(self) -> str:
        return self.__daynight

    @property
    def bright_t31(self) -> Optional[float]:
        return self.__bright_t31

    @property
    def bright_ti4(self) -> Optional[float]:
        return self.__bright_ti4

    @property
    def bright_ti5(self) -> Optional[float]:
        return self.__bright_ti5

    @property
    def acquired(self) -> datetime:
        return datetime.strptime(f"{self.acq_date} {self.acq_time}", "%Y-%m-%d %H%M")


class NASAFireLocationInputSchema(Schema):
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    brightness = fields.Float()
    scan = fields.Float(required=True)
    track = fields.Float(required=True)
    acq_date = fields.Str(required=True)
    acq_time = fields.Str(required=True)
    satellite = fields.Str(required=True)
    confidence = fields.Raw()
    version = fields.Str(required=True)
    bright_t31 = fields.Float()
    bright_ti4 = fields.Float()
    bright_ti5 = fields.Float()
    frp = fields.Float(required=True)
    daynight = fields.Str(required=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> NASAFireLocationInput:
        return NASAFireLocationInput(**values)


class TriggerMatchingInput(BaseInput):
    def __init__(
        self,
        dataset_harvest_ids: Optional[List[UUID]],
        subscription_ids: Optional[List[UUID]],
    ):
        super().__init__()

        self.__dataset_harvest_ids = dataset_harvest_ids
        self.__subscription_ids = subscription_ids

    @property
    def dataset_harvest_ids(self) -> Optional[List[UUID]]:
        return self.__dataset_harvest_ids

    @property
    def subscription_ids(self) -> Optional[List[UUID]]:
        return self.__subscription_ids


class TriggerMatchingInputSchema(Schema):
    subscription_ids = fields.List(fields.UUID(), allow_none=True)
    dataset_harvest_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerMatchingInput:
        return TriggerMatchingInput(**values)


class TriggerNotifyingInput(BaseInput):
    def __init__(
        self,
        subscription_match_ids: Optional[List[UUID]],
    ):
        super().__init__()

        self.__subscription_match_ids = subscription_match_ids

    @property
    def subscription_match_ids(self) -> Optional[List[UUID]]:
        return self.__subscription_match_ids


class TriggerNotifyingInputSchema(Schema):
    subscription_match_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerNotifyingInput:
        return TriggerNotifyingInput(**values)
