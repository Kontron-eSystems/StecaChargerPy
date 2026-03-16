# StecaChargerPy

Python client for the eSystems White Label Wallbox REST API with static methods for commonly used endpoints.

## Installation

Create a virtual environment and install the project in editable mode:

```
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

The client depends only on `requests` for HTTP communication. All API endpoints are hard-coded, so no external specification file is required.

## Usage

```python
from StecaChargerPy import WallboxClient

client = WallboxClient(
    "https://10.0.1.30/api/v2",
    username="username",
    password="password",
)

state = client.get_charging_state()
print(state)

# Set charging limits
limits = {"maxCurrentInA": 16, "minCurrentInA": 6}
client.set_charging_limits(limits)

# Set PV optimization mode
mode = {"enabled": True}
client.set_pv_optimization_mode(mode)
```

The client provides static methods for the following endpoints:

**Charging Methods:**
- `get_charging_state()` - Get current charging state
- `get_charging_limits()` - Get charging limits
- `set_charging_limits(limits)` - Set charging limits
- `get_charging_restrictions()` - Get active charging restrictions
- `get_charging_last_started_session()` - Get last charging session
- `get_charging_lifetime_stats()` - Get lifetime statistics
- `get_pv_optimization_mode()` - Get PV optimization mode
- `set_pv_optimization_mode(mode)` - Set PV optimization mode

**System Methods:**
- `get_system_electronic_typeplate()` - Get system typeplate
- `get_system_errors()` - Get system errors
- `delete_system_errors()` - Delete all system errors
- `get_system_energy_saving()` - Get energy saving status
- `set_system_energy_saving(enabled)` - Set energy saving status
- `get_system_device_temperatures()` - Get device temperatures
- `get_system_device_state()` - Get device state
- `get_relais_switch_state()` - Get relais switch state
- `set_relais_switch_state(state)` - Set relais switch state
- `get_relais_switch_enabled()` - Get relais switch enabled status
- `set_relais_switch_enabled(enabled)` - Set relais switch enabled status
- `get_system_socket_outlet()` - Get socket outlet information
- `set_system_socket_outlet(settings)` - Set socket outlet settings
- `get_system_energy_management_enabled()` - Get energy management status
- `set_system_energy_management_enabled(enabled)` - Set energy management status
- `get_system_update_available()` - Get system update availability
- `get_system_update_auto_update()` - Get automatic update setting
- `set_system_update_auto_update(enabled)` - Set automatic update setting

All methods support optional `query`, `headers`, `timeout`, and other parameters
via keyword arguments.

For advanced scenarios (multiple clients sharing the same credentials), the
`WallboxAuthenticator` class is available. Pass an authenticator instance
to `WallboxClient` to reuse sessions or manage tokens manually.

Refer to `examples/example.py` for a complete runnable example.

## Development

Run the test-suite via:

```
pytest
```