import pytest

from StecaChargerPy import ApiError, WallboxClient


def _build_client() -> WallboxClient:
    return WallboxClient("https://wallbox.local/api/v2")


def test_get_charging_state_returns_json(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/state",
        json={"status": "charging"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    payload = client.get_charging_state()

    assert payload == {"status": "charging"}


def test_unexpected_status_raises_api_error(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/state",
        json={"detail": "boom"},
        status_code=500,
        headers={"Content-Type": "application/json"},
    )

    with pytest.raises(ApiError) as exc_info:
        client.get_charging_state()

    assert exc_info.value.status_code == 500
    assert "GET /charging/state" in str(exc_info.value)


def test_client_login_sets_authorization_header(requests_mock) -> None:
    client = _build_client()

    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-123"},
    )

    token = client.login("user", "pass")
    assert token == "token-123"

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/state",
        json={"status": "charging"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    client.get_charging_state()

    assert requests_mock.last_request.headers.get("Authorization") == "Bearer token-123"


def test_client_auto_login_when_credentials_provided(requests_mock) -> None:
    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-123"},
    )

    client = WallboxClient(
        "https://wallbox.local/api/v2",
        username="user",
        password="pass",
    )

    assert client.token == "token-123"

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/state",
        json={"status": "charging"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    client.get_charging_state()

    assert requests_mock.last_request.headers.get("Authorization") == "Bearer token-123"


def test_set_charging_limits_sends_put_request(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/charging/limits",
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    limits = {"maxCurrentInA": 16, "minCurrentInA": 6}
    client.set_charging_limits(limits)

    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == limits


def test_set_pv_optimization_mode_sends_put_request(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/charging/pvoptimization/mode",
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    mode = {"enabled": True, "strategy": "max_pv"}
    client.set_pv_optimization_mode(mode)

    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == mode


def test_set_charging_limits_with_authentication(requests_mock) -> None:
    client = _build_client()

    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-456"},
    )

    client.login("user", "pass")

    requests_mock.put(
        "https://wallbox.local/api/v2/charging/limits",
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    limits = {"maxCurrentInA": 20}
    client.set_charging_limits(limits)

    assert requests_mock.last_request.headers.get("Authorization") == "Bearer token-456"
    assert requests_mock.last_request.json() == limits


def test_set_pv_optimization_mode_with_authentication(requests_mock) -> None:
    client = _build_client()

    requests_mock.post(
        "https://wallbox.local/api/v2/jwt/login",
        status_code=200,
        headers={"Authorization": "Bearer token-789"},
    )

    client.login("user", "pass")

    requests_mock.put(
        "https://wallbox.local/api/v2/charging/pvoptimization/mode",
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    mode = {"enabled": False}
    client.set_pv_optimization_mode(mode)

    assert requests_mock.last_request.headers.get("Authorization") == "Bearer token-789"
    assert requests_mock.last_request.json() == mode


def test_get_charging_restrictions(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/restrictions",
        json={"restrictions": []},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_charging_restrictions()
    assert result == {"restrictions": []}


def test_get_charging_lifetime_stats(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/charging/lifetime-stats",
        json={"totalEnergyCharged": 1234.5},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_charging_lifetime_stats()
    assert result == {"totalEnergyCharged": 1234.5}


def test_get_system_errors(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/errors",
        json={"errors": []},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_errors()
    assert result == {"errors": []}


def test_delete_system_errors(requests_mock) -> None:
    client = _build_client()

    requests_mock.delete(
        "https://wallbox.local/api/v2/system/errors",
        status_code=200,
    )

    client.delete_system_errors()
    assert requests_mock.last_request.method == "DELETE"


def test_get_system_energy_saving(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/energy-saving",
        json={"enabled": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_energy_saving()
    assert result == {"enabled": True}


def test_set_system_energy_saving(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/energy-saving",
        status_code=200,
    )

    client.set_system_energy_saving({"enabled": False})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"enabled": False}


def test_get_system_device_temperatures(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/device-temperatures",
        json={"cpuTemp": 45.2},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_device_temperatures()
    assert result == {"cpuTemp": 45.2}


def test_get_system_device_state(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/device-state",
        json={"state": "ready"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_device_state()
    assert result == {"state": "ready"}


def test_get_relais_switch_state(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/relais-switch/state",
        json={"state": "on"},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_relais_switch_state()
    assert result == {"state": "on"}


def test_set_relais_switch_state(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/relais-switch/state",
        status_code=200,
    )

    client.set_relais_switch_state({"state": "off"})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"state": "off"}


def test_get_relais_switch_enabled(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/relais-switch/enabled",
        json={"enabled": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_relais_switch_enabled()
    assert result == {"enabled": True}


def test_set_relais_switch_enabled(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/relais-switch/enabled",
        status_code=200,
    )

    client.set_relais_switch_enabled({"enabled": False})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"enabled": False}


def test_get_system_socket_outlet(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/socket-outlet",
        json={"outletEnabled": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_socket_outlet()
    assert result == {"outletEnabled": True}


def test_set_system_socket_outlet(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/socket-outlet",
        status_code=200,
    )

    client.set_system_socket_outlet({"outletEnabled": False})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"outletEnabled": False}


def test_get_system_energy_management_enabled(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/energy-management/enabled",
        json={"enabled": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_energy_management_enabled()
    assert result == {"enabled": True}


def test_set_system_energy_management_enabled(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/energy-management/enabled",
        status_code=200,
    )

    client.set_system_energy_management_enabled({"enabled": False})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"enabled": False}


def test_get_system_update_available(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/update/available",
        json={"updateAvailable": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_update_available()
    assert result == {"updateAvailable": True}


def test_get_system_update_auto_update(requests_mock) -> None:
    client = _build_client()

    requests_mock.get(
        "https://wallbox.local/api/v2/system/update/auto-update",
        json={"enabled": True},
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

    result = client.get_system_update_auto_update()
    assert result == {"enabled": True}


def test_set_system_update_auto_update(requests_mock) -> None:
    client = _build_client()

    requests_mock.put(
        "https://wallbox.local/api/v2/system/update/auto-update",
        status_code=200,
    )

    client.set_system_update_auto_update({"enabled": False})
    assert requests_mock.last_request.method == "PUT"
    assert requests_mock.last_request.json() == {"enabled": False}

