import sys
import urllib.request

from endpoint.config import settings


PORT = settings.port
HEALTH_URL = f"http://localhost:{PORT}/health"
TIMEOUT = 5  # seconds


def health_check():
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=TIMEOUT) as response:
            status_code = response.getcode()
            if 200 <= status_code < 300:
                print("ok")
                sys.exit(0)
            else:
                print(status_code)
                sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    health_check()
