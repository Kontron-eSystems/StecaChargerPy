"""Client utilities for the eSystems White Label Wallbox REST API.

The package exposes a high level :class:`WallboxClient` that provides static
methods for commonly used REST endpoints with proper type hints and documentation.

The most important entry points are:

``WallboxClient`` -- an HTTP client with static methods for key endpoints.
``WallboxAuthenticator`` -- manages authentication and bearer tokens.

Usage example::

    from StecaChargerPy import WallboxClient

    client = WallboxClient("https://10.0.1.30/api/v2",
                          username="user", password="pass")
    state = client.get_charging_state()

Responses are returned as decoded JSON dictionaries for flexibility.
"""

from .errors import ApiError
from .client import WallboxClient
from .authentication import AuthenticationError, WallboxAuthenticator

__all__ = [
    "AuthenticationError",
    "ApiError",
    "WallboxClient",
    "WallboxAuthenticator",
]

