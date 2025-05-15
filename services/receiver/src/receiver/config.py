from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    rabbitmq_queue: str


settings = Settings(_env_file=Path(__file__).parents[1] / ".env")  # noqa
