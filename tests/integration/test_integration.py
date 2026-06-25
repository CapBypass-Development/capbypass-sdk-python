"""Integration tests for CapBypass client against real API.

These tests require CAPBYPASS_TEST_KEY environment variable.
Run with: pytest tests/integration/ -v
"""

import os

import pytest

from capbypass import CapBypass
from capbypass.errors import AuthenticationError, ValidationError

# Skip all tests if CAPBYPASS_TEST_KEY not set
pytestmark = pytest.mark.skipif(
    not os.getenv("CAPBYPASS_TEST_KEY"),
    reason="CAPBYPASS_TEST_KEY environment variable not set",
)


@pytest.fixture
def client():
    """Create client with test API key."""
    api_key = os.getenv("CAPBYPASS_TEST_KEY")
    return CapBypass(api_key=api_key)


def test_get_balance(client):
    """Test getBalance() against real API."""
    balance = client.getBalance()
    assert isinstance(balance, float)
    assert balance >= 0


def test_create_task_recaptcha_v2_proxyless(client):
    """Test creating ReCaptchaV2TaskProxyLess task."""
    task_id = client.createTask({
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteURL": "https://www.google.com/recaptcha/api2/demo",
        "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
    })

    assert isinstance(task_id, str)
    assert len(task_id) > 0


def test_create_task_invalid_type(client):
    """Test creating task with invalid type."""
    with pytest.raises(ValidationError):
        client.createTask({
            "type": "InvalidTaskType",
            "websiteURL": "https://example.com",
        })


def test_invalid_api_key():
    """Test with invalid API key."""
    invalid_client = CapBypass(api_key="invalid-key-12345")

    with pytest.raises(AuthenticationError):
        invalid_client.getBalance()


def test_get_task_result(client):
    """Test getTaskResult() for a pending task."""
    # Create task first
    task_id = client.createTask({
        "type": "ReCaptchaV2TaskProxyLess",
        "websiteURL": "https://www.google.com/recaptcha/api2/demo",
        "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
    })

    # Get result (likely processing)
    result = client.getTaskResult(task_id)

    assert "status" in result
    assert result["status"] in ("processing", "ready", "failed")


@pytest.mark.slow
def test_solve_recaptcha_v2_proxyless(client):
    """Test solve() end-to-end for ReCaptchaV2TaskProxyLess.

    Note: This is a slow test (may take 30-60 seconds).
    """
    solution = client.solve(
        {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://www.google.com/recaptcha/api2/demo",
            "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        },
        timeout=120,
    )

    assert "gRecaptchaResponse" in solution
    assert isinstance(solution["gRecaptchaResponse"], str)
    assert len(solution["gRecaptchaResponse"]) > 100  # reCAPTCHA tokens are long


@pytest.mark.slow
def test_solve_aws_waf_proxyless(client):
    """Test solve() for AntiAwsWafTaskProxyLess.

    Note: This test requires a valid AWS WAF challenge URL.
    """
    # Skip if balance too low (AWS WAF tasks are expensive)
    balance = client.getBalance()
    if balance < 5.0:
        pytest.skip("Insufficient balance for AWS WAF test")

    solution = client.solve(
        {
            "type": "AntiAwsWafTaskProxyLess",
            "websiteURL": "https://example.com",  # Replace with actual site
            "awsChallengeJS": "https://example.com/challenge.js",  # Replace with actual URL
        },
        timeout=120,
    )

    assert "token" in solution
    assert "cookie" in solution
