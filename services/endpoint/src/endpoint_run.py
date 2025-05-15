import logging
import uvicorn

from endpoint.config import settings

logging.basicConfig(level="INFO")


if __name__ == "__main__":
    uvicorn.run("endpoint:app", host="0.0.0.0", port=settings.port, workers=2)
