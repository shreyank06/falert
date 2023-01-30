from asyncio import create_task
from json import loads
from uuid import UUID

from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.response import text, HTTPResponse, empty
from sqlalchemy import select
from sqlalchemy import func

from falert.backend.common.input import SubscriptionInputSchema
from falert.backend.common.output import (
    TriggerMatchingOutput,
    TriggerMatchingOutputSchema,
    StatisticsReadFireLocationOutput,
    StatisticsReadOutputSchema,
    StatisticsReadOutput,
)
from falert.backend.common.entity import (
    SubscriptionEntity,
    SubscriptionVertexEntity,
    FireLocationEntity,
    SubscriptionMatchEntity,
)


class BaseView(HTTPMethodView):
    pass


class PingView(BaseView):
    @staticmethod
    def get(_request: Request) -> HTTPResponse:
        return text("pong")


class SubscriptionCreateView(BaseView):
    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        subscription_input = SubscriptionInputSchema().load(loads(request.body))
        subscription_entity = SubscriptionEntity()

        for vertex in subscription_input.vertices:
            subscription_entity.subscription_vertices.append(
                SubscriptionVertexEntity(
                    longitude=vertex.longitude,
                    latitude=vertex.latitude,
                )
            )

        subscription_entity.phone_number = subscription_input.phone_number

        request.ctx.database_session.add(subscription_entity)
        await request.ctx.database_session.commit()

        trigger_matching_output = TriggerMatchingOutput(
            subscription_ids=[
                UUID(
                    str(subscription_entity.id)
                ),  # properly satisfy the type checker here
            ],
        )

        create_task(
            request.ctx.sender.send(
                "trigger_matching",
                TriggerMatchingOutputSchema().dumps(
                    trigger_matching_output,
                ),
            )
        )

        return empty(status=201)


class StatisticsReadView(BaseView):
    @staticmethod
    async def get(request: Request) -> HTTPResponse:
        subscriptions_count = (
            await request.ctx.database_session.execute(
                select(func.count()).select_from(SubscriptionEntity)
            )
        ).scalar()

        matches_count = (
            await request.ctx.database_session.execute(
                select(func.count()).select_from(SubscriptionMatchEntity)
            )
        ).scalar()

        fire_locations_count = (
            await request.ctx.database_session.execute(
                select(func.count()).select_from(FireLocationEntity)
            )
        ).scalar()

        fire_location_entities = list(
            await request.ctx.database_session.execute(
                select(FireLocationEntity)
                .order_by(
                    FireLocationEntity.created.desc(),
                    FireLocationEntity.acquired.desc(),
                    FireLocationEntity.latitude.asc(),
                    FireLocationEntity.longitude.asc(),
                )
                .limit(5)
            )
        )

        fire_locations = list(
            map(
                lambda x: StatisticsReadFireLocationOutput(
                    x[0].acquired, x[0].latitude, x[0].longitude
                ),
                fire_location_entities,
            )
        )

        statistics_read_output = StatisticsReadOutput(
            fire_locations,
            subscriptions_count,
            fire_locations_count,
            matches_count,
        )

        return text(
            StatisticsReadOutputSchema().dumps(statistics_read_output),
            headers={
                "Content-Type": "application/json",
            },
            status=200,
        )
