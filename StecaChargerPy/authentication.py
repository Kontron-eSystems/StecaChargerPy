"""Authentication helpers for the Wallbox REST API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from weakref import WeakSet

import requests

from .errors import ApiError

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .client import WallboxClient

__all__ = ["AuthenticationError", "WallboxAuthenticator"]


class AuthenticationError(ApiError):
    """Raised when authentication against the Wallbox fails."""


@dataclass(slots=True)
class WallboxAuthenticator:
    """Manage login/logout workflows and bearer token lifecycle."""

    base_url: str
    session: requests.Session = field(default_factory=requests.Session)
    verify: bool | str = True
    user_agent: str = "StecaChargerPy/0.1.0"
    default_timeout: Optional[float | tuple[float, float]] = 10.0
    _token: Optional[str] = field(init=False, default=None, repr=False)
    _attached_clients: WeakSet["WallboxClient"] = field(init=False, default_factory=WeakSet, repr=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    @property
    def token(self) -> Optional[str]:
        """Return the currently stored bearer token if available."""

        return self._token

    def login(
        self,
        username: str,
        password: str,
        *,
        timeout: Optional[float | tuple[float, float]] = None,
    ) -> str:
        """Authenticate a user and persist the returned bearer token."""

        url = f"{self.base_url}/jwt/login"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.user_agent,
        }
        response = self.session.post(
            url,
            data={"user": username, "pass": password},
            headers=headers,
            timeout=timeout if timeout is not None else self.default_timeout,
            verify=self.verify,
        )

        if response.status_code != 200:
            raise AuthenticationError(
                "Login failed",
                status_code=response.status_code,
                response=response,
            )

        token = response.headers.get("Authorization")
        if not token:
            raise AuthenticationError(
                "Login succeeded but Authorization header is missing",
                status_code=response.status_code,
                response=response,
            )

        self.set_token(_extract_bearer(token))
        return self._token

    def attach_to_client(self, client: "WallboxClient") -> None:
        """Connect a ``WallboxClient`` instance to this authenticator."""

        self._attached_clients.add(client)
        client.session = self.session
        client.verify = self.verify
        client._set_bearer_token(self._token)

    def logout(
        self,
        *,
        timeout: Optional[float | tuple[float, float]] = None,
    ) -> None:
        """Invalidate the current bearer token via the logout endpoint."""

        if not self._token:
            return

        url = f"{self.base_url}/jwt/logout"
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Authorization": f"Bearer {self._token}",
        }
        response = self.session.post(
            url,
            headers=headers,
            timeout=timeout if timeout is not None else self.default_timeout,
            verify=self.verify,
        )

        if response.status_code not in {200, 204}:
            raise AuthenticationError(
                "Logout failed",
                status_code=response.status_code,
                response=response,
            )

        self.set_token(None)

    def set_token(
        self,
        token: Optional[str],
        *,
        source: Optional["WallboxClient"] = None,
    ) -> None:
        self._token = token
        self._propagate_token(source=source)

    def _propagate_token(self, *, source: Optional["WallboxClient"] = None) -> None:
        for client in list(self._attached_clients):
            if client is source:
                continue
            client._set_bearer_token(self._token)


def _extract_bearer(header_value: str) -> str:
    prefix = "Bearer "
    if header_value.startswith(prefix):
        return header_value[len(prefix) :].strip()
    return header_value.strip()

