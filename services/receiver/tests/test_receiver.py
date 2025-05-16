import pytest
import json
from aio_pika import IncomingMessage

# The function to test
from receiver.receiver import process_message

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_incoming_message(mocker):
    """
    Fixture to create a mock aio_pika.IncomingMessage.
    It includes a mock for the `process()` async context manager.
    """
    message = mocker.MagicMock(spec=IncomingMessage)
    context_manager_mock = mocker.AsyncMock()
    context_manager_mock.__aenter__.return_value = None
    context_manager_mock.__aexit__.return_value = None
    message.process.return_value = context_manager_mock
    return message


async def test_process_message_success(mock_incoming_message, mocker, caplog):
    """
    Test successful processing of a valid message.
    """
    count_value = 42
    message_data = {"count": count_value}
    # In the SUT, message_body is the decoded string, message is the loaded
    # dict.
    message_body_str = json.dumps(message_data)
    mock_incoming_message.body = message_body_str.encode("utf-8")

    mocked_random_val = 0.5
    mocker.patch(
        "receiver.receiver.random.random", return_value=mocked_random_val
    )
    mock_sleep = mocker.patch("receiver.receiver.asyncio.sleep")

    await process_message(mock_incoming_message)

    mock_sleep.assert_called_once_with(mocked_random_val)
    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()


async def test_process_message_unicode_decode_error(
    mock_incoming_message, caplog
):
    """
    Test processing a message with invalid UTF-8 body.
    """
    invalid_body_bytes = b"\x80\xc2"  # Invalid UTF-8 sequence
    mock_incoming_message.body = invalid_body_bytes

    with pytest.raises(UnicodeDecodeError):
        await process_message(mock_incoming_message)

    assert (
        f"Failed to decode message bytes {invalid_body_bytes!r}" in caplog.text
    )
    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()


async def test_process_message_empty_body_bytes(mock_incoming_message, caplog):
    """
    Test processing a message with an empty byte string body (b'').
    This should trigger the `else` path of `if msg.body:`.
    """
    mock_incoming_message.body = b""

    with pytest.raises(ValueError, match="Empty message body"):
        await process_message(mock_incoming_message)

    assert f"Empty message body. msg={mock_incoming_message!r}" in caplog.text
    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()


async def test_process_message_none_body(mock_incoming_message, caplog):
    """
    Test processing a message where msg.body is None.
    This should also trigger the `else` path of `if msg.body:`.
    """
    mock_incoming_message.body = None

    with pytest.raises(ValueError, match="Empty message body"):
        await process_message(mock_incoming_message)

    assert f"Empty message body. msg={mock_incoming_message!r}" in caplog.text
    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()


async def test_process_message_missing_count_key(
    mock_incoming_message, caplog
):
    """
    Test processing a message that is valid JSON but missing the 'count' key.
    random.random and asyncio.sleep should NOT be called in this case.
    """
    # This is the Python dictionary that results from json.loads
    message_as_dict = {"other_key": "some_value"}
    message_body_str = json.dumps(message_as_dict)
    mock_incoming_message.body = message_body_str.encode("utf-8")

    with pytest.raises(KeyError, match="'count'"):
        await process_message(mock_incoming_message)

    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()


async def test_process_message_invalid_json_string(
    mock_incoming_message, caplog
):
    """
    Test processing a message with a body that is not valid JSON.
    random.random and asyncio.sleep should NOT be called.
    """
    invalid_json_body_str = "this is not valid json"
    mock_incoming_message.body = invalid_json_body_str.encode("utf-8")

    with pytest.raises(json.JSONDecodeError):
        await process_message(mock_incoming_message)

    mock_incoming_message.process.assert_called_once()
    mock_incoming_message.process.return_value.__aenter__.assert_called_once()
    mock_incoming_message.process.return_value.__aexit__.assert_called_once()
