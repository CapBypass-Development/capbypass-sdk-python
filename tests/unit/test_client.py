"""Unit tests for CapBypass client."""

import pytest
import responses

from capbypass import CapBypass
from capbypass.errors import (
    AuthenticationError,
    GatewayError,
    InsufficientBalanceError,
    InternalError,
    NetworkError,
    ParseError,
    RateLimitError,
    ServerError,
    SolverError,
    TaskNotFoundError,
    TimeoutError,
    ValidationError,
)


@pytest.fixture
def client():
    """Create test client."""
    return CapBypass(api_key="test-key")


@responses.activate
def test_create_task_success(client):
    """Test successful task creation."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 0, "taskId": "test-task-id-123"},
        status=200,
    )

    task_id = client.createTask({
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteURL": "https://example.com",
        "websiteKey": "test-key",
    })

    assert task_id == "test-task-id-123"


@responses.activate
def test_create_task_invalid_key(client):
    """Test task creation with invalid API key."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_KEY_DOES_NOT_EXIST",
            "errorDescription": "Account not found",
        },
        status=200,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.createTask({"type": "ReCaptchaV2TaskProxyLess"})

    assert exc_info.value.error_code == "ERROR_KEY_DOES_NOT_EXIST"


@responses.activate
def test_create_task_zero_balance(client):
    """Test task creation with zero balance."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_ZERO_BALANCE",
            "errorDescription": "Insufficient balance",
        },
        status=200,
    )

    with pytest.raises(InsufficientBalanceError):
        client.createTask({"type": "ReCaptchaV2TaskProxyLess"})


@responses.activate
def test_create_task_invalid_data(client):
    """Test task creation with invalid task data."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_INVALID_TASK_DATA",
            "errorDescription": "Invalid task type",
        },
        status=200,
    )

    with pytest.raises(ValidationError):
        client.createTask({"type": "InvalidTaskType"})


@responses.activate
def test_create_task_invalid_developer_key(client):
    """Test task creation with invalid developer key."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_INVALID_DEVELOPER_KEY",
            "errorDescription": "Invalid developer key",
        },
        status=200,
    )

    with pytest.raises(ValidationError) as exc_info:
        client.createTask({"type": "ReCaptchaV2TaskProxyLess"})

    assert exc_info.value.error_code == "ERROR_INVALID_DEVELOPER_KEY"


@responses.activate
def test_create_task_proxy_connection_failed(client):
    """Test task creation when the customer proxy could not be reached."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_PROXY_CONNECTION_FAILED",
            "errorDescription": "Could not connect through proxy",
        },
        status=200,
    )

    with pytest.raises(ValidationError) as exc_info:
        client.createTask({"type": "ReCaptchaV2Task"})

    assert exc_info.value.error_code == "ERROR_PROXY_CONNECTION_FAILED"


@responses.activate
def test_create_task_proxy_banned(client):
    """Test task creation when the target blocked the customer proxy IP."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_PROXY_BANNED",
            "errorDescription": "Proxy IP blocked by target",
        },
        status=200,
    )

    with pytest.raises(ValidationError) as exc_info:
        client.createTask({"type": "ReCaptchaV2Task"})

    assert exc_info.value.error_code == "ERROR_PROXY_BANNED"


@responses.activate
def test_get_task_result_processing(client):
    """Test getting task result in processing state."""
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={"errorId": 0, "status": "processing"},
        status=200,
    )

    result = client.getTaskResult("test-task-id")
    assert result["status"] == "processing"


@responses.activate
def test_get_task_result_ready(client):
    """Test getting task result when ready."""
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={
            "errorId": 0,
            "status": "ready",
            "solution": {"gRecaptchaResponse": "test-token"},
        },
        status=200,
    )

    result = client.getTaskResult("test-task-id")
    assert result["status"] == "ready"
    assert result["solution"]["gRecaptchaResponse"] == "test-token"


@responses.activate
def test_get_task_result_not_found(client):
    """Test getting result for non-existent task."""
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={
            "errorId": 16,
            "errorCode": "ERROR_TASK_NOT_FOUND",
            "errorDescription": "Task not found",
        },
        status=200,
    )

    with pytest.raises(TaskNotFoundError):
        client.getTaskResult("invalid-task-id")


@responses.activate
def test_solve_success(client):
    """Test solve() with successful resolution."""
    # Mock createTask
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 0, "taskId": "test-task-id"},
        status=200,
    )

    # Mock first getTaskResult (processing)
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={"errorId": 0, "status": "processing"},
        status=200,
    )

    # Mock second getTaskResult (ready)
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={
            "errorId": 0,
            "status": "ready",
            "solution": {"gRecaptchaResponse": "solved-token"},
        },
        status=200,
    )

    solution = client.solve({
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteURL": "https://example.com",
        "websiteKey": "test-key",
    })

    assert solution["gRecaptchaResponse"] == "solved-token"


@responses.activate
def test_solve_failed(client):
    """Test solve() when task fails."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 0, "taskId": "test-task-id"},
        status=200,
    )

    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={
            "errorId": 0,
            "status": "failed",
            "errorDescription": "CAPTCHA unsolvable",
        },
        status=200,
    )

    with pytest.raises(SolverError):
        client.solve({"type": "ReCaptchaV2TaskProxyLess"})


@responses.activate
def test_solve_timeout(client):
    """Test solve() timeout."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 0, "taskId": "test-task-id"},
        status=200,
    )

    # Always return processing (will trigger timeout)
    responses.post(
        "https://api.capbypass.pro/getTaskResult",
        json={"errorId": 0, "status": "processing"},
        status=200,
    )

    with pytest.raises(TimeoutError):
        client.solve({"type": "ReCaptchaV2TaskProxyLess"}, timeout=3)


@responses.activate
def test_get_balance_success(client):
    """Test getBalance() success."""
    responses.post(
        "https://api.capbypass.pro/getBalance",
        json={"errorId": 0, "balance": 42.5000},
        status=200,
    )

    balance = client.getBalance()
    assert balance == 42.5


@responses.activate
def test_gateway_error_retry(client):
    """Test retry logic on gateway errors."""
    # First attempt: 503
    responses.post(
        "https://api.capbypass.pro/getBalance",
        status=503,
    )

    # Second attempt: success
    responses.post(
        "https://api.capbypass.pro/getBalance",
        json={"errorId": 0, "balance": 10.0},
        status=200,
    )

    balance = client.getBalance()
    assert balance == 10.0


@responses.activate
def test_gateway_error_max_retries(client):
    """Test gateway error after max retries."""
    # All attempts: 503
    for _ in range(4):
        responses.post(
            "https://api.capbypass.pro/getBalance",
            status=503,
        )

    with pytest.raises(GatewayError):
        client.getBalance()


def test_network_error(client, monkeypatch):
    """Test network connection error."""
    import requests

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.ConnectionError("Connection refused")

    # Mock the session.post to raise ConnectionError
    monkeypatch.setattr(client.session, "post", mock_post)

    with pytest.raises(NetworkError):
        client.getBalance()

    # Verify it tried max_retries + 1 times (initial + 3 retries)
    assert call_count == 4


def test_client_no_api_key():
    """Test client initialization without API key."""
    with pytest.raises(ValueError, match="API key is required"):
        CapBypass()


def test_client_from_env_var(monkeypatch):
    """Test client initialization from environment variable."""
    monkeypatch.setenv("CAPBYPASS_API_KEY", "env-key")
    client = CapBypass()
    assert client.api_key == "env-key"


def test_client_param_over_env(monkeypatch):
    """Test parameter takes priority over env var."""
    monkeypatch.setenv("CAPBYPASS_API_KEY", "env-key")
    client = CapBypass(api_key="param-key")
    assert client.api_key == "param-key"


@pytest.fixture
def fast_retry(monkeypatch):
    """Make retry backoff instant + deterministic so retry paths run fast."""
    import capbypass.client as client_module

    monkeypatch.setattr(client_module.time, "sleep", lambda _s: None)
    monkeypatch.setattr(client_module.random, "uniform", lambda _a, _b: 0.0)


# ---------------------------------------------------------------------------
# getPricing / _make_get_request (lines 83-143, 435-436)
# ---------------------------------------------------------------------------


@responses.activate
def test_get_pricing_success(client):
    """getPricing() returns the pricing list from the public GET endpoint."""
    responses.get(
        "https://api.capbypass.pro/pricing",
        json={
            "pricing": [
                {"task_type": "ReCaptchaV2TaskProxyLess", "user_cost": 0.001},
                {"task_type": "AntiAwsWafTask", "user_cost": 0.002},
            ]
        },
        status=200,
    )

    pricing = client.getPricing()
    assert isinstance(pricing, list)
    assert pricing[0]["task_type"] == "ReCaptchaV2TaskProxyLess"
    assert pricing[1]["user_cost"] == 0.002


@responses.activate
def test_get_pricing_missing_key_defaults_empty(client):
    """getPricing() defaults to [] when the response has no 'pricing' key."""
    responses.get(
        "https://api.capbypass.pro/pricing",
        json={"errorId": 0},
        status=200,
    )

    assert client.getPricing() == []


@responses.activate
def test_get_request_gateway_retry_then_success(client, fast_retry):
    """GET helper retries on 503 then succeeds (covers retry branch)."""
    responses.get("https://api.capbypass.pro/pricing", status=503)
    responses.get(
        "https://api.capbypass.pro/pricing",
        json={"pricing": [{"task_type": "x", "user_cost": 0.1}]},
        status=200,
    )

    pricing = client.getPricing()
    assert pricing[0]["task_type"] == "x"


@responses.activate
def test_get_request_gateway_max_retries(client, fast_retry):
    """GET helper raises GatewayError after exhausting retries on 5xx gateway."""
    for _ in range(4):
        responses.get("https://api.capbypass.pro/pricing", status=502)

    with pytest.raises(GatewayError):
        client.getPricing()


@responses.activate
def test_get_request_server_error(client):
    """GET helper raises ServerError (no retry) on HTTP 500."""
    responses.get("https://api.capbypass.pro/pricing", status=500)

    with pytest.raises(ServerError):
        client.getPricing()


@responses.activate
def test_get_request_parse_error(client):
    """GET helper raises ParseError on malformed JSON body."""
    responses.get(
        "https://api.capbypass.pro/pricing",
        body="this-is-not-json",
        status=200,
        content_type="application/json",
    )

    with pytest.raises(ParseError):
        client.getPricing()


def test_get_request_connection_error_retries(client, monkeypatch, fast_retry):
    """GET helper retries on ConnectionError, then raises NetworkError."""
    import requests

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.ConnectionError("refused")

    monkeypatch.setattr(client.session, "get", mock_get)

    with pytest.raises(NetworkError):
        client.getPricing()

    assert call_count == 4  # initial + 3 retries


def test_get_request_timeout_retries(client, monkeypatch, fast_retry):
    """GET helper retries on Timeout, then raises NetworkError."""
    import requests

    call_count = 0

    def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(client.session, "get", mock_get)

    with pytest.raises(NetworkError):
        client.getPricing()

    assert call_count == 4


def test_get_request_generic_request_exception(client, monkeypatch):
    """GET helper wraps a generic RequestException as NetworkError (no retry)."""
    import requests

    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(client.session, "get", mock_get)

    with pytest.raises(NetworkError):
        client.getPricing()


# ---------------------------------------------------------------------------
# _make_request POST error branches (lines 192, 198, 206-207, 224-241)
# ---------------------------------------------------------------------------


@responses.activate
def test_post_server_error(client):
    """POST helper raises ServerError on HTTP 500."""
    responses.post("https://api.capbypass.pro/getBalance", status=500)

    with pytest.raises(ServerError):
        client.getBalance()


@responses.activate
def test_post_rate_limit(client):
    """POST helper raises RateLimitError on HTTP 429."""
    responses.post("https://api.capbypass.pro/getBalance", status=429)

    with pytest.raises(RateLimitError):
        client.getBalance()


@responses.activate
def test_post_parse_error(client):
    """POST helper raises ParseError on malformed JSON body."""
    responses.post(
        "https://api.capbypass.pro/getBalance",
        body="<<not json>>",
        status=200,
        content_type="application/json",
    )

    with pytest.raises(ParseError):
        client.getBalance()


def test_post_timeout_retries(client, monkeypatch, fast_retry):
    """POST helper retries on Timeout, then raises NetworkError."""
    import requests

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr(client.session, "post", mock_post)

    with pytest.raises(NetworkError):
        client.getBalance()

    assert call_count == 4


def test_post_generic_request_exception(client, monkeypatch):
    """POST helper wraps a generic RequestException as NetworkError (no retry)."""
    import requests

    def mock_post(*args, **kwargs):
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(client.session, "post", mock_post)

    with pytest.raises(NetworkError):
        client.getBalance()


# ---------------------------------------------------------------------------
# createTask developerKey payload branch (line 322)
# ---------------------------------------------------------------------------


@responses.activate
def test_create_task_includes_developer_key():
    """createTask() adds developerKey to the payload when configured."""
    client = CapBypass(api_key="test-key", developer_key="dev-key-xyz")

    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 0, "taskId": "task-with-devkey"},
        status=200,
    )

    task_id = client.createTask({"type": "ReCaptchaV2TaskProxyLess"})

    assert task_id == "task-with-devkey"
    sent = responses.calls[0].request.body
    assert b"developerKey" in sent
    assert b"dev-key-xyz" in sent


# ---------------------------------------------------------------------------
# _handle_error_response additional branches
# ---------------------------------------------------------------------------


@responses.activate
def test_create_task_proxy_not_defined(client):
    """ERROR_PROXY_NOT_DEFINED maps to ValidationError."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 1,
            "errorCode": "ERROR_PROXY_NOT_DEFINED",
            "errorDescription": "Proxy is required for this task type",
        },
        status=200,
    )

    with pytest.raises(ValidationError) as exc_info:
        client.createTask({"type": "ReCaptchaV2Task"})

    assert exc_info.value.error_code == "ERROR_PROXY_NOT_DEFINED"


@responses.activate
def test_create_task_unknown_error_code_maps_internal(client):
    """An unmapped error code falls back to InternalError with details preserved."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={
            "errorId": 99,
            "errorCode": "ERROR_TASK_QUEUE_FULL",
            "errorDescription": "Queue is full",
        },
        status=200,
    )

    with pytest.raises(InternalError) as exc_info:
        client.createTask({"type": "ReCaptchaV2TaskProxyLess"})

    assert exc_info.value.error_code == "ERROR_TASK_QUEUE_FULL"
    assert exc_info.value.error_id == 99
    assert exc_info.value.error_description == "Queue is full"


@responses.activate
def test_error_response_with_missing_fields_defaults(client):
    """An error with errorId set but no code/description uses safe defaults."""
    responses.post(
        "https://api.capbypass.pro/createTask",
        json={"errorId": 5},
        status=200,
    )

    with pytest.raises(InternalError) as exc_info:
        client.createTask({"type": "ReCaptchaV2TaskProxyLess"})

    assert exc_info.value.error_code == "UNKNOWN_ERROR"
    assert exc_info.value.error_description == "Unknown error"
