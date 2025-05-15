import asyncio
import logging
from logging import getLogger
from pathlib import Path
from typing import Awaitable, Callable

import aio_pika
from aio_pika import ExchangeType, DeliveryMode, Message, IncomingMessage
from aio_pika.exceptions import ChannelClosed
from pydantic_settings import BaseSettings, SettingsConfigDict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    after_log,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    max_retries: int = 10

    rabbitmq_host: str
    rabbitmq_exchange: str


settings = Settings(_env_file=Path(__file__).parent / ".env")  # noqa
logger = getLogger("commons.rabbitmq_utils")


rabbitmq_host = settings.rabbitmq_host
connection_url = f"amqp://guest:guest@{rabbitmq_host}/"


@retry(
    wait=wait_random_exponential(),
    stop=stop_after_attempt(settings.max_retries),
    after=after_log(logger, logging.WARNING),
)
async def make_connection():
    """Make connection with exponential retry."""
    return await aio_pika.connect(connection_url)


async def send_to_exchange(message_body: bytes | str, routing_key: str):
    """Sends a message to the exchange.

    Args:
        message_body: The message body to send.
        routing_key: The routing key for the message. This is the name of the
            queue in our case.
    """
    connection = await make_connection()

    async with connection:
        channel = await connection.channel()
        try:
            exchange = await channel.declare_exchange(
                name=settings.rabbitmq_exchange,
                type=ExchangeType.DIRECT,
                durable=True,
            )
        except ChannelClosed as e:
            logger.error(
                f"Failed to declare exchange "
                f"{settings.rabbitmq_exchange}: {e}"
            )
            raise e

        # Convert to bytes if necessary
        if isinstance(message_body, str):
            message_body = message_body.encode("utf-8")
        message = Message(message_body, delivery_mode=DeliveryMode.PERSISTENT)

        await exchange.publish(message, routing_key=routing_key)
        logger.debug(
            f"Message sent to exchange '{settings.rabbitmq_exchange}' "
            f"with routing key '{routing_key}'."
        )


async def rabbitmq_consumer(
    rabbitmq_queue: str,
    on_message: Callable[[IncomingMessage], Awaitable[None]],
):
    connection = await make_connection()

    async with connection:
        channel = await connection.channel()

        try:
            rmq_exchange = await channel.declare_exchange(
                settings.rabbitmq_exchange, ExchangeType.DIRECT, durable=True
            )
        except ChannelClosed as e:
            logger.error(
                f"Failed to declare exchange "
                f"{settings.rabbitmq_exchange}: {e}"
            )
            raise e

        try:
            queue = await channel.declare_queue(rabbitmq_queue, durable=True)
        except ChannelClosed as e:
            logger.error(f"Failed to declare queue {rabbitmq_queue}: {e}")
            raise e

        await queue.bind(rmq_exchange)

        await queue.consume(on_message)
        logger.debug("Waiting for messages. To exit, press CTRL+C")

        # Keep the consumer running indefinitely.
        await asyncio.Future()
