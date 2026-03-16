import pytest

from StecaChargerPy import (
    ApiError,
    AuthenticationError,
    WallboxAuthenticator,
    WallboxClient,
)


def _make_client_and_auth() -> tuple[WallboxClient, WallboxAuthenticator]:
    authenticator = WallboxAuthenticator("https://wallbox.local/api/v2")
    client = WallboxClient(
        "https://wallbox.local/api/v2",
        session=authenticator.session,
    )
    return client, authenticator


def test_login_extracts_bearer_token(requests_mock) -> None:
    client, auth = _make_client_and_auth()

    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-123"},
    )

    token = auth.login("user", "pass")
    assert token == "token-123"

    auth.attach_to_client(client)

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/state",
        json={"status": "charging"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_charging_state()
    assert result == {"status": "charging"}


def test_login_without_authorization_header_raises(requests_mock) -> None:
    _, auth = _make_client_and_auth()
    requests_mock.post("https://wallbox.local/api/v2/jwt/login", status_code=200)

    with pytest.raises(AuthenticationError):
        auth.login("user", "pass")


def test_logout_clears_token(requests_mock) -> None:
    client, auth = _make_client_and_auth()

    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-123"},
    )
    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/logout",
        status_code=200,
    )

    auth.login("user", "pass")
    auth.attach_to_client(client)

    auth.logout()

    assert auth.token is None
    assert client.session is auth.session
    # client should not send Authorization header if token cleared
    with pytest.raises(ApiError):
        requests_mock.get(
            "https://wallbox.local/api/v2/charging/state",
            json={"status": "charging"},
            status_code=401,
            headers={"Content-Type": "application/json"},
        )
        client.get_charging_state()

