import logging
import sys
from pathlib import Path

from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.logging_v2.handlers import CloudLoggingHandler
from google.cloud.logging_v2.resource import Resource


def setup_logging(service_name: str, log_level: int):
    """
    Configures logging to send logs to Google Cloud Logging and the console.

    Authentication is handled in the following order:
    1. Looks for a service account key file named 'log-sa.json' in this
       directory.
    2. Falls back to Application Default Credentials (ADC) if the file is
       not found. This works automatically on most GCP services or with
       'gcloud auth application-default login'.
    3. Raises a RuntimeError if neither method provides credentials.

    Args:
        service_name: The name of the service, which will be attached
            as a label to all log entries for filtering.
        log_level: The minimum log level to capture (e.g., logging.INFO,
            logging.WARNING).
    """
    key_path = Path(__file__).parent / "log-sa.json"

    try:
        if key_path.exists():
            print(
                f"INFO: Authenticating logging with service account file at: "
                f"{key_path}"
            )
            credentials = (
                service_account.Credentials.from_service_account_file(key_path)
            )
        else:
            print(
                "INFO: 'log-sa.json' not found. Falling back to Application "
                "Default Credentials."
            )
            from google import auth

            credentials, _ = auth.default()
    except DefaultCredentialsError:
        print(
            "FATAL: Could not find any Google Cloud credentials.",
            file=sys.stderr,
        )
        print(
            "       Please run 'gcloud auth application-default login' or \n"
            "       place a 'log-sa.json' key file in the same directory\n"
            "       as this script.",
            file=sys.stderr,
        )
        raise RuntimeError(
            "Failed to initialize Google Cloud Logging due to "
            "missing credentials"
        )

    try:
        from google.cloud import logging as gcp_logging

        client = gcp_logging.Client(credentials=credentials)
    except Exception as e:
        print(
            f"FATAL: Failed to create Google Cloud Logging client. Error:\n"
            f"{e}"
        )
        raise RuntimeError("Failed to initialize Google Cloud Logging client")

    gcp_handler = CloudLoggingHandler(
        client=client,
        resource=Resource(
            type="global", labels={"resource_service": service_name}
        ),
        labels={"service": service_name},
    )

    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s -%(name)s:%(lineno)d - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(gcp_handler)
    root_logger.addHandler(console_handler)

    print("INFO: Setting log levels for noisy packages to CRITICAL.")
    logging.getLogger("pymongo").setLevel(logging.CRITICAL)
    logging.getLogger("aio_pika").setLevel(logging.CRITICAL)
    logging.getLogger("aiormq").setLevel(logging.CRITICAL)
    logging.getLogger("pika").setLevel(logging.CRITICAL)

    print(f"INFO: Logging successfully configured for service {service_name}")
