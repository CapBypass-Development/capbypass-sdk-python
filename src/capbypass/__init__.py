"""CapBypass Python SDK

Official Python SDK for CapBypass CAPTCHA solving API.
"""

from .client import CapBypass
from .errors import (
    CapBypassError,
    AuthenticationError,
    InsufficientBalanceError,
    ValidationError,
    TaskNotFoundError,
    SolverError,
    TimeoutError,
    InternalError,
    NetworkError,
    GatewayError,
    ServerError,
    RateLimitError,
    ParseError,
)
from .types import TaskType

__version__ = "1.0.0"
__all__ = [
    "CapBypass",
    "CapBypassError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "ValidationError",
    "TaskNotFoundError",
    "SolverError",
    "TimeoutError",
    "InternalError",
    "NetworkError",
    "GatewayError",
    "ServerError",
    "RateLimitError",
    "ParseError",
    "TaskType",
]
