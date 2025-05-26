import asyncio
import logging

from receiver import process_message
from receiver.config import settings
from commons.rabbitmq_utils import rabbitmq_consumer
from commons.logging.setup_logging import setup_logging


setup_logging(service_name="receiver", log_level=logging.INFO)
logger = logging.getLogger(__name__)


def on_startup():
    logger.info("Starting up receiver service...")

    logger.info(f"Loading with settings\n{settings.model_dump_json(indent=2)}")


if __name__ == "__main__":
    on_startup()
    asyncio.run(rabbitmq_consumer(settings.rabbitmq_queue, process_message))
