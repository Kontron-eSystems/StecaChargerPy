"""HTTP client for the eSystems White Label Wallbox REST API."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional

import requests

from .authentication import WallboxAuthenticator
from .errors import ApiError

__all__ = ["ApiError", "WallboxClient"]


class WallboxClient:
    """HTTP client for the eSystems White Label Wallbox REST API."""

    def __init__(
        self,
        base_url: str,
        *,
        session: Optional[requests.Session] = None,
        default_timeout: Optional[float | tuple[float, float]] = 10.0,
        verify: bool | str = True,
        user_agent: Optional[str] = None,
        authenticator: Optional[WallboxAuthenticator] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.default_timeout = default_timeout
        self.verify = verify
        self.user_agent = user_agent or "StecaChargerPy/0.1.0"
        self._bearer_token: Optional[str] = None
        if authenticator is None:
            authenticator = WallboxAuthenticator(
                self.base_url,
                session=self.session,
                verify=self.verify,
                user_agent=self.user_agent,
                default_timeout=self.default_timeout,
            )
        else:
            self.session = authenticator.session
            self.verify = authenticator.verify
            self.user_agent = authenticator.user_agent
            self.default_timeout = authenticator.default_timeout
        self.authenticator = authenticator
        self.authenticator.attach_to_client(self)

        if username and password:
            self.authenticator.login(username, password)

    def set_bearer_token(self, token: Optional[str]) -> None:
        """Store a bearer token that is automatically added to requests."""

        self._set_bearer_token(token)
        if self.authenticator:
            self.authenticator.set_token(token, source=self)

    def _set_bearer_token(self, token: Optional[str]) -> None:
        self._bearer_token = token

    @property
    def token(self) -> Optional[str]:
        return self._bearer_token

    def login(
        self,
        username: str,
        password: str,
        *,
        timeout: Optional[float | tuple[float, float]] = None,
    ) -> str:
        return self.authenticator.login(username, password, timeout=timeout)

    def logout(self, *, timeout: Optional[float | tuple[float, float]] = None) -> None:
        self.authenticator.logout(timeout=timeout)

    # Static method definitions for commonly used endpoints
    def get_charging_state(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get the current charging state.

        Returns:
            Dictionary containing the charging state information.
        """
        return self._make_request(
            "GET",
            "/charging/state",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_charging_limits(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get the current charging limits.

        Returns:
            Dictionary containing the charging limits.
        """
        return self._make_request(
            "GET",
            "/charging/limits",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_pv_optimization_mode(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get the PV optimization mode.

        Returns:
            Dictionary containing the PV optimization mode settings.
        """
        return self._make_request(
            "GET",
            "/charging/pvoptimization/mode",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_electronic_typeplate(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get the system electronic typeplate information.

        Returns:
            Dictionary containing the electronic typeplate data.
        """
        return self._make_request(
            "GET",
            "/system/electronic-typeplate",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_charging_last_started_session(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get information about the last started charging session.

        Returns:
            Dictionary containing the last charging session information.
        """
        return self._make_request(
            "GET",
            "/charging/last-started-session",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_charging_limits(
        self,
        limits: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set the charging limits.

        Args:
            limits: Dictionary containing the charging limits to set.

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/charging/limits",
            query=query,
            body=limits,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_pv_optimization_mode(
        self,
        mode: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set the PV optimization mode.

        Args:
            mode: Dictionary containing the PV optimization mode settings to set.

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/charging/pvoptimization/mode",
            query=query,
            body=mode,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_charging_restrictions(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get active charging restrictions.

        Returns:
            Dictionary containing the active charging restrictions.
        """
        return self._make_request(
            "GET",
            "/charging/restrictions",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_charging_lifetime_stats(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get lifetime statistics.

        Returns:
            Dictionary containing accumulated wallbox lifetime statistics.
        """
        return self._make_request(
            "GET",
            "/charging/lifetime-stats",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_errors(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get system errors.

        Returns:
            Dictionary containing the system errors.
        """
        return self._make_request(
            "GET",
            "/system/errors",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def delete_system_errors(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Delete all system errors.

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "DELETE",
            "/system/errors",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_energy_saving(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get energy saving enabled status.

        Returns:
            Dictionary containing the energy saving enabled status.
        """
        return self._make_request(
            "GET",
            "/system/energy-saving",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_system_energy_saving(
        self,
        enabled: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set energy saving enabled status.

        Args:
            enabled: Dictionary containing the enabled status (e.g., {"enabled": True}).

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/energy-saving",
            query=query,
            body=enabled,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_device_temperatures(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get device temperatures.

        Returns:
            Dictionary containing temperatures of different locations inside the device.
        """
        return self._make_request(
            "GET",
            "/system/device-temperatures",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_device_state(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get device state.

        Returns:
            Dictionary containing the device state.
        """
        return self._make_request(
            "GET",
            "/system/device-state",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_relais_switch_state(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get relais switch state.

        Returns:
            Dictionary containing the relais switch state.
        """
        return self._make_request(
            "GET",
            "/system/relais-switch/state",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_relais_switch_state(
        self,
        state: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set relais switch state.

        Args:
            state: Dictionary containing the relais switch state to set.

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/relais-switch/state",
            query=query,
            body=state,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_relais_switch_enabled(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get relais switch enabled status.

        Returns:
            Dictionary containing the relais switch enabled status.
        """
        return self._make_request(
            "GET",
            "/system/relais-switch/enabled",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_relais_switch_enabled(
        self,
        enabled: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set relais switch enabled status.

        Args:
            enabled: Dictionary containing the enabled status (e.g., {"enabled": True}).

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/relais-switch/enabled",
            query=query,
            body=enabled,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_socket_outlet(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get socket outlet information.

        Returns:
            Dictionary containing the socket outlet information.
        """
        return self._make_request(
            "GET",
            "/system/socket-outlet",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_system_socket_outlet(
        self,
        settings: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set socket outlet settings.

        Args:
            settings: Dictionary containing the socket outlet settings to set.

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/socket-outlet",
            query=query,
            body=settings,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_energy_management_enabled(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get energy management enabled status.

        Returns:
            Dictionary containing the energy management enabled status.
        """
        return self._make_request(
            "GET",
            "/system/energy-management/enabled",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_system_energy_management_enabled(
        self,
        enabled: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set energy management enabled status.

        Args:
            enabled: Dictionary containing the enabled status (e.g., {"enabled": True}).

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/energy-management/enabled",
            query=query,
            body=enabled,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_update_available(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get system update settings available.

        Returns:
            Dictionary containing the system update availability information.
        """
        return self._make_request(
            "GET",
            "/system/update/available",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def get_system_update_auto_update(
        self,
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Get automatic update setting.

        Returns:
            Dictionary containing whether wallbox automatically installs update files.
        """
        return self._make_request(
            "GET",
            "/system/update/auto-update",
            query=query,
            body=None,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def set_system_update_auto_update(
        self,
        enabled: Mapping[str, Any],
        *,
        query: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected_status: Optional[Iterable[int]] = None,
        timeout: Optional[float | tuple[float, float]] = None,
        raw: bool = False,
    ) -> Any:
        """Set automatic update setting.

        Args:
            enabled: Dictionary containing the enabled status (e.g., {"enabled": True}).

        Returns:
            Dictionary containing the response, or None for 200 OK with no content.
        """
        return self._make_request(
            "PUT",
            "/system/update/auto-update",
            query=query,
            body=enabled,
            headers=headers,
            expected_status=expected_status or [200],
            timeout=timeout,
            raw=raw,
        )

    def _make_request(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Mapping[str, Any]],
        body: Optional[Any],
        headers: Optional[Mapping[str, str]],
        expected_status: Iterable[int],
        timeout: Optional[float | tuple[float, float]],
        raw: bool,
    ) -> Any:
        """Make an HTTP request to the wallbox API.

        Args:
            method: HTTP method (GET, PUT, POST, DELETE, etc.)
            path: API path (e.g., "/charging/state")
            query: Optional query parameters
            body: Optional request body (will be JSON encoded)
            headers: Optional custom headers
            expected_status: List of expected HTTP status codes
            timeout: Optional timeout override
            raw: If True, return the raw response object

        Returns:
            Parsed JSON response or raw response object
        """
        url = f"{self.base_url}{path}"
        request_headers = self._build_headers(headers, body)

        response = self.session.request(
            method,
            url,
            params=query,
            json=body,
            headers=request_headers,
            timeout=timeout if timeout is not None else self.default_timeout,
            verify=self.verify,
        )

        if response.status_code not in expected_status:
            raise ApiError(
                f"Unexpected status {response.status_code} for {method} {path}",
                status_code=response.status_code,
                response=response,
            )

        if raw:
            return response

        if response.status_code == 204 or not response.content:
            return None

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.content

    def _build_headers(
        self,
        custom_headers: Optional[Mapping[str, str]],
        body: Optional[Any],
    ) -> Dict[str, str]:
        """Build HTTP headers for a request."""
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if body is not None:
            headers.setdefault("Content-Type", "application/json")
        if self._bearer_token:
            headers.setdefault("Authorization", f"Bearer {self._bearer_token}")
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "WallboxClient":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()
