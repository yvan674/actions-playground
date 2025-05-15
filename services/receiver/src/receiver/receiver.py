import asyncio
import json
import random
from logging import getLogger

from aio_pika import IncomingMessage


logger = getLogger(__name__)


async def process_message(msg: IncomingMessage):
    async with msg.process():
        # Decode the message and check if it has a JSON body with key "count"
        if msg.body:
            try:
                # Assuming the message body is a JSON string
                message_body = msg.body.decode("utf-8")
                logger.info(f"Received message: {message_body}")
            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode message bytes {msg.body}: {e}")
                raise e
        else:
            logger.error(f"Empty message body. {msg=}")
            raise ValueError(f"Empty message body. {msg=}")

        message = json.loads(message_body)
        try:
            count = message["count"]
        except KeyError as e:
            logger.error(f"Message does not contain key 'count': {message=}")
            raise e

        wait_for = random.random()
        await asyncio.sleep(wait_for)

        logger.info(f"{wait_for=}, {count=}")
