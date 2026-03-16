"""Error classes shared across the Wallbox client package."""

from __future__ import annotations

from typing import Any, Optional

import requests

__all__ = ["ApiError"]


class ApiError(RuntimeError):
    """Raised when the Wallbox responds with an unexpected status code."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response: Optional[requests.Response] = None,
        operation: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.operation = operation

