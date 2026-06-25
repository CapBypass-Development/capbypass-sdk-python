"""CapBypass Python SDK

Official Python SDK for CapBypass CAPTCHA solving API.
"""

from .client import CapBypass
from .errors import (
    AuthenticationError,
    CapBypassError,
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
