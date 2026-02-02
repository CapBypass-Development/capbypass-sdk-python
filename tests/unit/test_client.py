"""Unit tests for CapBypass client."""

import pytest
import responses
from responses import matchers

from capbypass import CapBypass
from capbypass.errors import (
    AuthenticationError,
    InsufficientBalanceError,
    ValidationError,
    TaskNotFoundError,
    SolverError,
    TimeoutError,
    NetworkError,
    GatewayError,
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


@responses.activate
def test_network_error(client):
    """Test network connection error."""
    responses.post(
        "https://api.capbypass.pro/getBalance",
        body=ConnectionError("Connection refused"),
    )

    # Add retries
    for _ in range(3):
        responses.post(
            "https://api.capbypass.pro/getBalance",
            body=ConnectionError("Connection refused"),
        )

    with pytest.raises(NetworkError):
        client.getBalance()


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
