"""CapBypass Python SDK

Official Python SDK for CapBypass CAPTCHA solving API.
"""

from ._version import __version__
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

__all__ = [
    "__version__",
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
