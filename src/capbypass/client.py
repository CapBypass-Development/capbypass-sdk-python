"""CapBypass API client."""

import os
import time
import random
from typing import Dict, Any, Optional

import requests

from .errors import (
    AuthenticationError,
    InsufficientBalanceError,
    ValidationError,
    TaskNotFoundError,
    SolverError,
    TimeoutError as CapBypassTimeoutError,
    InternalError,
    NetworkError,
    GatewayError,
    ServerError,
    RateLimitError,
    ParseError,
)


class CapBypass:
    """CapBypass API client for CAPTCHA solving.

    Args:
        api_key: CapBypass API key. If not provided, reads from CAPBYPASS_API_KEY env var.
        base_url: API gateway URL. Defaults to production gateway.

    Raises:
        ValueError: If api_key is not provided and CAPBYPASS_API_KEY env var is not set.

    Example:
        >>> from capbypass import CapBypass
        >>> client = CapBypass(api_key="your-api-key")
        >>> result = client.solve({
        ...     "type": "ReCaptchaV2TaskProxyLess",
        ...     "websiteURL": "https://example.com",
        ...     "websiteKey": "site-key"
        ... })
        >>> print(result["gRecaptchaResponse"])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.capbypass.pro",
        developer_key: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("CAPBYPASS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide via constructor or CAPBYPASS_API_KEY env var."
            )
        self.developer_key = developer_key or os.getenv("CAPBYPASS_DEVELOPER_KEY")

        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "capbypass-sdk-python/1.0.0",
        })

    def _make_get_request(
        self,
        endpoint: str,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP GET request with retry logic.

        Args:
            endpoint: API endpoint path (e.g., "/pricing")
            max_retries: Maximum number of retry attempts for network failures

        Returns:
            Parsed JSON response
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0

        while attempt <= max_retries:
            try:
                response = self.session.get(url, timeout=30)

                if response.status_code in (502, 503, 504):
                    if attempt < max_retries:
                        backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                        time.sleep(backoff)
                        attempt += 1
                        continue
                    raise GatewayError(
                        error_code="GATEWAY_ERROR",
                        error_description=f"Gateway error: HTTP {response.status_code}",
                    )

                if response.status_code == 500:
                    raise ServerError(
                        error_code="SERVER_ERROR",
                        error_description="Internal server error",
                    )

                try:
                    return response.json()
                except ValueError as e:
                    raise ParseError(
                        error_code="PARSE_ERROR",
                        error_description=f"Malformed JSON response: {e}",
                    )

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                    time.sleep(backoff)
                    attempt += 1
                    continue
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Connection failed: {e}",
                )

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                    time.sleep(backoff)
                    attempt += 1
                    continue
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Request timeout: {e}",
                )

            except requests.exceptions.RequestException as e:
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Request failed: {e}",
                )

        raise NetworkError(
            error_code="NETWORK_ERROR",
            error_description="Max retries exceeded",
        )

    def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            endpoint: API endpoint path (e.g., "/createTask")
            payload: Request JSON payload
            max_retries: Maximum number of retry attempts for network failures

        Returns:
            Parsed JSON response

        Raises:
            NetworkError: On connection failures
            GatewayError: On 502/503/504 responses
            ServerError: On 500 responses
            RateLimitError: On 429 responses
            ParseError: On malformed JSON responses
        """
        url = f"{self.base_url}{endpoint}"
        attempt = 0

        while attempt <= max_retries:
            try:
                response = self.session.post(url, json=payload, timeout=30)

                # Handle HTTP-layer errors
                if response.status_code in (502, 503, 504):
                    if attempt < max_retries:
                        # Exponential backoff with jitter for gateway errors
                        backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                        time.sleep(backoff)
                        attempt += 1
                        continue
                    raise GatewayError(
                        error_code="GATEWAY_ERROR",
                        error_description=f"Gateway error: HTTP {response.status_code}",
                    )

                if response.status_code == 500:
                    raise ServerError(
                        error_code="SERVER_ERROR",
                        error_description="Internal server error",
                    )

                if response.status_code == 429:
                    raise RateLimitError(
                        error_code="RATE_LIMIT",
                        error_description="Rate limit exceeded",
                    )

                # Parse JSON response
                try:
                    return response.json()
                except ValueError as e:
                    raise ParseError(
                        error_code="PARSE_ERROR",
                        error_description=f"Malformed JSON response: {e}",
                    )

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                    time.sleep(backoff)
                    attempt += 1
                    continue
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Connection failed: {e}",
                )

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    backoff = min(10, 2 ** attempt) + random.uniform(0, 1)
                    time.sleep(backoff)
                    attempt += 1
                    continue
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Request timeout: {e}",
                )

            except requests.exceptions.RequestException as e:
                raise NetworkError(
                    error_code="NETWORK_ERROR",
                    error_description=f"Request failed: {e}",
                )

        # Should never reach here, but just in case
        raise NetworkError(
            error_code="NETWORK_ERROR",
            error_description="Max retries exceeded",
        )

    def _handle_error_response(self, response: Dict[str, Any]) -> None:
        """Handle error responses from API.

        Args:
            response: API response dict

        Raises:
            AuthenticationError: On ERROR_KEY_DOES_NOT_EXIST
            InsufficientBalanceError: On ERROR_ZERO_BALANCE
            ValidationError: On ERROR_INVALID_TASK_DATA
            TaskNotFoundError: On ERROR_TASK_NOT_FOUND
            SolverError: On ERROR_CAPTCHA_UNSOLVABLE
            CapBypassTimeoutError: On ERROR_TIMEOUT
            InternalError: On ERROR_INTERNAL or other errors
        """
        error_id = response.get("errorId", 0)
        if error_id == 0:
            return  # Success

        error_code = response.get("errorCode", "UNKNOWN_ERROR")
        error_description = response.get("errorDescription", "Unknown error")

        # Map error codes to exception classes
        error_map = {
            "ERROR_KEY_DOES_NOT_EXIST": AuthenticationError,
            "ERROR_ZERO_BALANCE": InsufficientBalanceError,
            "ERROR_INVALID_TASK_DATA": ValidationError,
            "TASK_TYPE_COMING_SOON": ValidationError,
            "TASK_TYPE_INACTIVE": ValidationError,
            "ERROR_TASK_NOT_FOUND": TaskNotFoundError,
            "ERROR_CAPTCHA_UNSOLVABLE": SolverError,
            "ERROR_TIMEOUT": CapBypassTimeoutError,
            "ERROR_INTERNAL": InternalError,
        }

        exception_class = error_map.get(error_code, InternalError)
        raise exception_class(
            error_code=error_code,
            error_description=error_description,
            error_id=error_id,
        )

    def createTask(self, task: Dict[str, Any]) -> str:
        """Create a CAPTCHA solving task.

        Args:
            task: Task configuration dict with "type" and task-specific parameters

        Returns:
            Task ID (UUID string)

        Raises:
            AuthenticationError: Invalid API key
            InsufficientBalanceError: Account balance is zero
            ValidationError: Invalid task data

        Example:
            >>> task_id = client.createTask({
            ...     "type": "ReCaptchaV2TaskProxyLess",
            ...     "websiteURL": "https://example.com",
            ...     "websiteKey": "site-key"
            ... })
        """
        payload = {
            "clientKey": self.api_key,
            "task": task,
        }
        if self.developer_key:
            payload["developerKey"] = self.developer_key

        response = self._make_request("/createTask", payload)
        self._handle_error_response(response)

        return response["taskId"]

    def getTaskResult(self, task_id: str) -> Dict[str, Any]:
        """Get result of a CAPTCHA solving task.

        Args:
            task_id: Task ID returned from createTask()

        Returns:
            Dict with "status" (processing/ready/failed), "solution" (if ready), error details (if failed)

        Raises:
            TaskNotFoundError: Task ID does not exist
            AuthenticationError: Invalid API key

        Example:
            >>> result = client.getTaskResult(task_id)
            >>> if result["status"] == "ready":
            ...     print(result["solution"])
        """
        payload = {
            "clientKey": self.api_key,
            "taskId": task_id,
        }

        response = self._make_request("/getTaskResult", payload)
        self._handle_error_response(response)

        return response

    def solve(
        self,
        task: Dict[str, Any],
        timeout: int = 120,
    ) -> Dict[str, Any]:
        """Create task and poll until solved (auto-polling).

        Args:
            task: Task configuration dict
            timeout: Maximum time to wait in seconds (default: 120)

        Returns:
            Solution dict (varies by task type)

        Raises:
            CapBypassTimeoutError: Task exceeded timeout
            SolverError: Task failed to solve
            AuthenticationError: Invalid API key
            InsufficientBalanceError: Account balance is zero
            ValidationError: Invalid task data

        Example:
            >>> solution = client.solve({
            ...     "type": "ReCaptchaV2TaskProxyLess",
            ...     "websiteURL": "https://example.com",
            ...     "websiteKey": "site-key"
            ... })
            >>> print(solution["gRecaptchaResponse"])
        """
        # Create task
        task_id = self.createTask(task)

        # Poll with adaptive intervals
        start_time = time.time()
        attempt = 0

        while True:
            # Check timeout (wall-clock time)
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise CapBypassTimeoutError(
                    error_code="TIMEOUT",
                    error_description=f"Task exceeded timeout of {timeout}s",
                )

            # Get task result
            result = self.getTaskResult(task_id)
            status = result.get("status")

            if status == "ready":
                return result.get("solution", {})

            if status == "failed":
                error_description = result.get("errorDescription", "Task failed")
                raise SolverError(
                    error_code="SOLVER_ERROR",
                    error_description=error_description,
                )

            # Adaptive polling: min(5, ceil(attempt / 2)) seconds
            # Attempts 1-2 → 1s, 3-4 → 2s, 5-6 → 3s, 7+ → 5s
            attempt += 1
            poll_interval = min(5, (attempt + 1) // 2)
            time.sleep(poll_interval)

    def getPricing(self) -> list:
        """Get pricing for all task types.

        This is a public endpoint and does not require authentication.

        Returns:
            List of dicts with "task_type" (str) and "user_cost" (float)

        Example:
            >>> pricing = client.getPricing()
            >>> for item in pricing:
            ...     print(f"{item['task_type']}: ${item['user_cost']}")
        """
        response = self._make_get_request("/pricing")
        return response.get("pricing", [])

    def getBalance(self) -> float:
        """Get account balance.

        Returns:
            Account balance as float

        Raises:
            AuthenticationError: Invalid API key

        Example:
            >>> balance = client.getBalance()
            >>> print(f"Balance: ${balance:.4f}")
        """
        payload = {
            "clientKey": self.api_key,
        }

        response = self._make_request("/getBalance", payload)
        self._handle_error_response(response)

        return float(response["balance"])
