from logging import getLogger
from typing import Annotated

from fastapi import FastAPI, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from commons.rabbitmq_utils import send_to_exchange
from endpoint.config import settings


logger = getLogger(__name__)
num_calls = 0


class Count(BaseModel):
    count: int


app = FastAPI(title="Counting API", summary="Counts the number of calls made.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)


@app.get("/api/count")
def get_count(x_real_ip: Annotated[str | None, Header()] = None) -> Count:
    """Gets the number of times the endpoint has been called."""
    logger.info(f"GET to get_count with {num_calls=}")
    logger.info(f"Request from {x_real_ip}")
    return Count(count=num_calls)


@app.post("/api/count/increment")
async def increment_count(
    background_task: BackgroundTasks,
    x_real_ip: Annotated[str | None, Header()] = None,
) -> Count:
    """Increments and gets the number of times the endpoint has been called."""
    global num_calls

    logger.info(f"POST to increment {num_calls=}")
    logger.info(f"Request from {x_real_ip}")

    num_calls += 1

    return_val = Count(count=num_calls)

    message = return_val.model_dump_json()

    background_task.add_task(send_to_exchange, message, settings.rabbitmq_queue)

    return return_val


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}
