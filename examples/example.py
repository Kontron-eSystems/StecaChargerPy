"""Minimal example using the Wallbox client."""

from StecaChargerPy import WallboxClient


def main() -> None:
    base_url = "https://funbox-vwbx-00000115/api/v2"
    client = WallboxClient(
        base_url,
        username="technician",
        password="SWE4dev!",
        verify=False,  # Skip SSL certificate verification
    )

    # Authentication happens during client instantiation. Handle errors here if
    # desired in production code.

    # The example assumes the mock server provided in the OpenAPI document is
    # running locally. Replace the base URL with the IP address of the actual
    # Wallbox installation when available.
    state = client.get_charging_state()
    print("Current charging state:", state)

    charging_limits = client.get_charging_limits()
    print("Charging limits:", charging_limits)

    pv_mode = client.get_pv_optimization_mode()
    print("PV optimization mode:", pv_mode)

    typeplate = client.get_system_electronic_typeplate()
    print("Electronic typeplate:", typeplate)

    last_session = client.get_charging_last_started_session()
    print("Last started session:", last_session)


if __name__ == "__main__":
    main()

