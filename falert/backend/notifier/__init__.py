from datetime import timedelta, datetime
from typing import List, Optional
from uuid import UUID

from boto3 import client
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload, aliased

from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.entity import (
    SubscriptionEntity,
    SubscriptionMatchEntity,
    SubscriptionNotificationEntity,
)
from falert.backend.common.input import TriggerNotifyingInputSchema
from falert.backend.common.messenger import AsyncpgReceiver


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        self.__receiver = None
        # pylint: disable=unused-private-member
        self.__sns_client = client(
            "sns",
            aws_access_key_id=self._configuration.aws_access_key_id,
            aws_secret_access_key=self._configuration.aws_secret_access_key,
            region_name=self._configuration.aws_region_name,
        )

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            self.__receiver = AsyncpgReceiver(
                raw_connection.dbapi_connection.driver_connection
            )

            await self.__handle_notifying(None)

            while True:
                trigger_notifying_input = TriggerNotifyingInputSchema().loads(
                    await self.__receiver.receive("trigger_notifying")
                )

                await self.__handle_notifying(
                    trigger_notifying_input.subscription_match_ids
                )

    async def __handle_notifying(self, subscription_match_ids: Optional[List[UUID]]):
        self._logger.info("Start notifying")

        session_maker = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        subscription_entities = []

        async with session_maker() as database_session:
            if subscription_match_ids is None or len(subscription_match_ids) == 0:
                self._logger.info(
                    # pylint: disable=line-too-long
                    "Fetch subscriptions with matches from the last 6 hours and without notifications from the last 6 hours"
                )

                now = datetime.utcnow()

                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .outerjoin(SubscriptionMatchEntity)
                            .outerjoin(SubscriptionNotificationEntity)
                            .options(
                                joinedload(SubscriptionEntity.subscription_matches)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_notifications
                                )
                            )
                            .where(
                                and_(
                                    SubscriptionMatchEntity.created
                                    >= now - timedelta(hours=6),
                                    or_(
                                        SubscriptionNotificationEntity.created
                                        <= now - timedelta(hours=6),
                                        # pylint: disable=singleton-comparison
                                        SubscriptionNotificationEntity.id == None,
                                    ),
                                )
                            )
                        )
                    ).unique()
                )
            else:
                self._logger.info(
                    # pylint: disable=line-too-long
                    "Fetch subscriptions with match ids %s and without notifications from the last 6 hours",
                    ", ".join(map(str, subscription_match_ids)),
                )

                now = datetime.utcnow()

                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .outerjoin(SubscriptionMatchEntity)
                            .outerjoin(SubscriptionNotificationEntity)
                            .options(
                                joinedload(SubscriptionEntity.subscription_matches)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_notifications
                                )
                            )
                            .where(
                                and_(
                                    SubscriptionMatchEntity.id.in_(
                                        subscription_match_ids,
                                    ),
                                    or_(
                                        SubscriptionNotificationEntity.created
                                        <= now - timedelta(hours=6),
                                        # pylint: disable=singleton-comparison
                                        SubscriptionNotificationEntity.id == None,
                                    ),
                                )
                            )
                        )
                    ).unique()
                )

                self._logger.info(
                    "Fetch all subscriptions with subscription match ids %s",
                    ", ".join(map(str, subscription_match_ids)),
                )

        self._logger.info(
            "Notify %s subscription(s)",
            len(subscription_entities),
        )

        for (subscription_entity,) in subscription_entities:
            self._logger.info(
                "Notify subscription id %s",
                subscription_entity.id,
            )

            try:
                async with session_maker() as database_session:
                    self.__sns_client.publish(
                        PhoneNumber=subscription_entity.phone_number,
                        Message="There have been detected several fire locations",
                    )

                    subscription_entity.subscription_notifications.append(
                        SubscriptionNotificationEntity()
                    )

                    database_session.add(subscription_entity)
                    await database_session.commit()
            # pylint: disable=broad-except
            except BaseException as error:
                self._logger.error(
                    "Error notifying subscription %s (%s)",
                    subscription_entity.id,
                    error,
                )

        self._logger.info("Finish notifying")
