from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    rabbitmq_queue: str

    port: int = 8080
    num_workers: int = 2


settings = Settings(_env_file=Path(__file__).parents[2] / ".env")  # noqa
