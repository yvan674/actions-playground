import os
import pytest

from endpoint.config import Settings


@pytest.fixture(autouse=True)
def cleanup_env():
    """Fixture to clean up environment variables before and after each test."""
    # List of environment variables used by the Settings class
    settings_vars = ["RABBITMQ_QUEUE", "PORT", "NUM_WORKERS"]

    # Clean up environment variables that might interfere
    original_env = os.environ.copy()
    for key in settings_vars:
        if key in os.environ:
            del os.environ[key]

    yield

    # Restore environment variables to their original state after the test
    os.environ.clear()
    os.environ.update(original_env)


def test_settings_from_environment_variables(monkeypatch):
    """Tests loading settings from environment variables."""
    monkeypatch.setenv("RABBITMQ_QUEUE", "test_queue_from_env")
    monkeypatch.setenv("PORT", "9090")
    monkeypatch.setenv("NUM_WORKERS", "10")
    # Add an extra variable to check if it's ignored
    monkeypatch.setenv("ANOTHER_EXTRA", "ignore_this_too")

    settings = Settings()

    assert settings.rabbitmq_queue == "test_queue_from_env"
    assert settings.port == 9090
    assert settings.num_workers == 10


def test_settings_with_defaults(monkeypatch):
    """Ensure default values used when optional settings are not provided."""
    # Only set the required variable
    monkeypatch.setenv("RABBITMQ_QUEUE", "only_required")

    # Initialize Settings - defaults should be picked up for port and
    # num_workers
    settings = Settings()

    assert settings.rabbitmq_queue == "only_required"
    assert settings.port == 8080  # Default value
    assert settings.num_workers == 2  # Default value


def test_required_setting_missing(monkeypatch):
    """Tests missing required setting ."""
    # Ensure the required variable is NOT set
    if "RABBITMQ_QUEUE" in os.environ:
        del os.environ["RABBITMQ_QUEUE"]

    # PydanticSettings will raise a ValueError if a required field is missing
    with pytest.raises(ValueError):
        Settings()


def test_extra_settings_are_ignored(monkeypatch):
    """Tests that extra environment variables are ignored."""
    monkeypatch.setenv("RABBITMQ_QUEUE", "test_queue")
    monkeypatch.setenv("EXTRA_ENV_VAR_1", "ignore_me")
    monkeypatch.setenv("YET_ANOTHER", "ignore_me_too")
    monkeypatch.setenv("PORT", "8100")  # Include a valid one too

    # Initialize Settings
    settings = Settings()

    assert settings.rabbitmq_queue == "test_queue"
    assert settings.port == 8100
    # Check that the extra env vars were not added to the settings object
    with pytest.raises(AttributeError):
        settings.EXTRA_ENV_VAR_1
    with pytest.raises(AttributeError):
        settings.YET_ANOTHER
