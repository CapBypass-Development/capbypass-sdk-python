"""Exception classes for CapBypass SDK."""


class CapBypassError(Exception):
    """Base exception for all CapBypass errors.

    Attributes:
        error_code: Capsolver-compatible error code (e.g., "ERROR_KEY_DOES_NOT_EXIST")
        error_description: Human-readable error message
        error_id: Numeric error ID from API response
    """

    def __init__(self, error_code: str = None, error_description: str = None, error_id: int = None):
        self.error_code = error_code
        self.error_description = error_description or str(error_code)
        self.error_id = error_id
        super().__init__(self.error_description)


class AuthenticationError(CapBypassError):
    """Raised when API key is invalid or missing."""
    pass


class InsufficientBalanceError(CapBypassError):
    """Raised when account balance is zero or insufficient."""
    pass


class ValidationError(CapBypassError):
    """Raised when task data is invalid."""
    pass


class TaskNotFoundError(CapBypassError):
    """Raised when task ID does not exist."""
    pass


class SolverError(CapBypassError):
    """Raised when CAPTCHA cannot be solved."""
    pass


class TimeoutError(CapBypassError):
    """Raised when solve() exceeds timeout."""
    pass


class InternalError(CapBypassError):
    """Raised when server encounters an internal error."""
    pass


# HTTP-layer errors


class NetworkError(CapBypassError):
    """Raised when network connection fails (DNS, refused, timeout)."""
    pass


class GatewayError(CapBypassError):
    """Raised when gateway returns 502/503/504 (retryable)."""
    pass


class ServerError(CapBypassError):
    """Raised when server returns 500 error."""
    pass


class RateLimitError(CapBypassError):
    """Raised when request is rate-limited (429)."""
    pass


class ParseError(CapBypassError):
    """Raised when response JSON is malformed."""
    pass
