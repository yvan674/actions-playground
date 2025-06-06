import logging
import uvicorn

from endpoint.config import settings
from commons.logging.setup_logging import setup_logging

setup_logging(service_name="endpoint", log_level=logging.INFO)


if __name__ == "__main__":
    uvicorn.run(
        "endpoint:app", host="0.0.0.0", port=settings.port, log_config=None
    )
