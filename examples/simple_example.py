"""Simple example showing a single API call to get charging state."""

from StecaChargerPy import WallboxClient


def main() -> None:
    # Configure your Wallbox connection
    base_url = "https://vwbx-00001010.local/api/v2"
    username = "technician"
    password = "AwZeBKx85hY*pd"

    # Create the client (authentication happens automatically)
    client = WallboxClient(
        base_url,
        username=username,
        password=password,
        verify=False,  # Skip SSL certificate verification for self-signed certs
    )

    # Make a single API call to get the charging state
    state = client.get_charging_state()

    # Print the result
    print("Charging State:")
    print(state)


if __name__ == "__main__":
    main()
