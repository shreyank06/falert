from datetime import datetime
from uuid import UUID
from typing import List, Any, Optional, Mapping

from marshmallow import Schema, fields, post_load


class BaseOutput:
    pass


class TriggerMatchingOutput(BaseOutput):
    def __init__(
        self,
        dataset_harvest_ids: Optional[List[UUID]] = None,
        subscription_ids: Optional[List[UUID]] = None,
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


class TriggerMatchingOutputSchema(Schema):
    subscription_ids = fields.List(fields.UUID(), allow_none=True)
    dataset_harvest_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerMatchingOutput:
        return TriggerMatchingOutput(**values)


class TriggerNotifyingOutput(BaseOutput):
    def __init__(
        self,
        subscription_match_ids: Optional[List[UUID]],
    ):
        super().__init__()

        self.__subscription_match_ids = subscription_match_ids

    @property
    def subscription_match_ids(self) -> Optional[List[UUID]]:
        return self.__subscription_match_ids


class TriggerNotifyingOutputSchema(Schema):
    subscription_match_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerNotifyingOutput:
        return TriggerNotifyingOutput(**values)


class StatisticsReadFireLocationOutput(BaseOutput):
    def __init__(self, acquired: datetime, latitude: float, longitude: float) -> None:
        super().__init__()

        self.__acquired = acquired
        self.__latitude = latitude
        self.__longitude = longitude

    @property
    def acquired(self) -> datetime:
        return self.__acquired

    @property
    def latitude(self) -> float:
        return self.__latitude

    @property
    def longitude(self) -> float:
        return self.__longitude


class StatisticsReadFireLocationOutputSchema(Schema):
    acquired = fields.DateTime(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> "StatisticsReadFireLocationOutputSchema":
        return StatisticsReadFireLocationOutputSchema(**values)


class StatisticsReadOutput(BaseOutput):
    def __init__(
        self,
        fire_locations: List["StatisticsReadFireLocationOutput"],
        subscriptions_count: int,
        fire_locations_count: int,
        matches_count: int,
    ) -> None:
        self.__fire_locations = fire_locations
        self.__subscriptions_count = subscriptions_count
        self.__fire_locations_count = fire_locations_count
        self.__matches_count = matches_count

    @property
    def fire_locations(self) -> List["StatisticsReadFireLocationOutput"]:
        return self.__fire_locations

    @property
    def subscriptions_count(self) -> int:
        return self.__subscriptions_count

    @property
    def fire_locations_count(self) -> int:
        return self.__fire_locations_count

    @property
    def matches_count(self) -> int:
        return self.__matches_count


class StatisticsReadOutputSchema(Schema):
    fire_locations = fields.List(
        fields.Nested(StatisticsReadFireLocationOutputSchema, required=True)
    )
    subscriptions_count = fields.Int(required=True)
    fire_locations_count = fields.Int(required=True)
    matches_count = fields.Int(required=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> "StatisticsReadOutput":
        return StatisticsReadOutput(**values)
