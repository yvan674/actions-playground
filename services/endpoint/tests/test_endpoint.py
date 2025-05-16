import pytest
from fastapi.testclient import TestClient
from endpoint.endpoint import app
import endpoint.endpoint

# Constant for our mocked RabbitMQ queue name
MOCKED_RABBITMQ_QUEUE = "test_mocked_queue"


@pytest.fixture(scope="function")
def client():
    """
    Pytest fixture to create a TestClient instance for each test function.
    It also resets the num_calls global in the app module before each test.
    """
    # Reset num_calls before each test run for isolation
    endpoint.endpoint.num_calls = 0
    yield TestClient(app)
    # Teardown code can go here if needed


def test_read_health(client):
    """
    Test the /health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_initial_count(client):
    """Test GET /api/count initially. Expects count to be 0."""
    response = client.get("/api/count")
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_get_count_with_x_real_ip(client):
    """
    Test GET /api/count with X-Real-IP header.
    Count should be 0 initially.
    """
    response = client.get("/api/count", headers={"X-Real-IP": "192.168.1.1"})
    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_increment_count(client, mocker):
    """Test POST /api/count/increment.

    It should increment the count, return the new count,
    and call the mocked send_to_exchange with the mocked queue and correct
    JSON string message.
    """
    # Mock the send_to_exchange function within endpoint.endpoint
    mocked_send_function = mocker.patch("endpoint.endpoint.send_to_exchange")

    # Mock settings.rabbitmq_queue specifically where it's used in
    # endpoint.endpoint
    mocker.patch(
        "endpoint.endpoint.settings.rabbitmq_queue", MOCKED_RABBITMQ_QUEUE
    )

    # First increment
    response = client.post("/api/count/increment")
    assert response.status_code == 200

    expected_count = 1
    expected_response_data = {
        "count": expected_count
    }  # This is the expected JSON body of the HTTP response
    assert response.json() == expected_response_data

    # Verify send_to_exchange was called correctly
    # The message sent to RabbitMQ is the Pydantic model dumped to a
    # JSON string.
    expected_rabbitmq_message = '{"count":' + str(expected_count) + "}"

    mocked_send_function.assert_called_once_with(
        expected_rabbitmq_message,
        MOCKED_RABBITMQ_QUEUE,
    )

    # Check count via GET to ensure state change
    response_get = client.get("/api/count")
    assert response_get.status_code == 200
    assert response_get.json() == {"count": expected_count}


def test_increment_count_with_x_real_ip(client, mocker):
    """
    Test POST /api/count/increment with X-Real-IP header.
    It should increment the count, return the new count,
    and call the mocked send_to_exchange with the mocked queue.
    """
    mocked_send_function = mocker.patch("endpoint.endpoint.send_to_exchange")
    mocker.patch(
        "endpoint.endpoint.settings.rabbitmq_queue", MOCKED_RABBITMQ_QUEUE
    )

    response = client.post(
        "/api/count/increment", headers={"X-Real-IP": "10.0.0.1"}
    )
    assert response.status_code == 200
    expected_count = 1
    expected_response_data = {"count": expected_count}
    assert response.json() == expected_response_data

    mocked_send_function.assert_called_once_with(
        '{"count":' + str(expected_count) + "}", MOCKED_RABBITMQ_QUEUE
    )


def test_get_count_after_multiple_increments(client, mocker):
    """Test GET /api/count after several increments within the same test.

    Ensures send_to_exchange is called for each increment with the correct
    details.
    """
    mocked_send_function = mocker.patch("endpoint.endpoint.send_to_exchange")
    mocker.patch(
        "endpoint.endpoint.settings.rabbitmq_queue", MOCKED_RABBITMQ_QUEUE
    )

    # First increment
    client.post("/api/count/increment")
    mocked_send_function.assert_called_with(
        '{"count":1}', MOCKED_RABBITMQ_QUEUE
    )

    # Second increment
    client.post("/api/count/increment")  # num_calls becomes 2
    mocked_send_function.assert_called_with(
        '{"count":2}', MOCKED_RABBITMQ_QUEUE
    )

    # Check final count
    response = client.get("/api/count")
    assert response.status_code == 200
    assert response.json() == {"count": 2}

    # Verify total calls
    assert mocked_send_function.call_count == 2


def test_increment_and_get_sequence(client, mocker):
    """
    Test a sequence of increment and get operations to ensure count consistency
    and correct calls to send_to_exchange.
    """
    mocked_send_function = mocker.patch("endpoint.endpoint.send_to_exchange")
    mocker.patch(
        "endpoint.endpoint.settings.rabbitmq_queue", MOCKED_RABBITMQ_QUEUE
    )

    # Initial state check (num_calls is 0 due to fixture)
    response_get1 = client.get("/api/count")
    assert response_get1.status_code == 200
    assert response_get1.json() == {"count": 0}

    # 1. Increment count
    response_post1 = client.post("/api/count/increment")
    assert response_post1.status_code == 200
    assert response_post1.json() == {"count": 1}
    # Check that send_to_exchange was called with the latest values
    mocked_send_function.assert_called_with(
        '{"count":1}', MOCKED_RABBITMQ_QUEUE
    )

    # 2. Get count again
    response_get2 = client.get("/api/count")
    assert response_get2.status_code == 200
    assert response_get2.json() == {"count": 1}

    # 3. Increment count again
    response_post2 = client.post(
        "/api/count/increment", headers={"X-Real-IP": "test-ip-123"}
    )
    assert response_post2.status_code == 200
    assert response_post2.json() == {"count": 2}
    mocked_send_function.assert_called_with(
        '{"count":2}', MOCKED_RABBITMQ_QUEUE
    )

    # 4. Final get count
    response_get3 = client.get(
        "/api/count", headers={"X-Real-IP": "test-ip-456"}
    )
    assert response_get3.status_code == 200
    assert response_get3.json() == {"count": 2}

    # Verify total calls to send_to_exchange
    assert mocked_send_function.call_count == 2
