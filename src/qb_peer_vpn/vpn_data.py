"""Module for ProtonVPN server data management."""

from typing import List, Dict, Optional
import requests
import json


class ProtonVPNData:
    """Manage ProtonVPN server data."""

    def __init__(self, data_url: Optional[str] = None):
        """Initialize with ProtonVPN data source.

        Args:
            data_url: URL to ProtonVPN server JSON data
        """
        self.data_url = data_url or (
            "https://raw.githubusercontent.com/Huzky/protonvpn-servers/main/servers.json"
        )
        self.servers = []

    def fetch_servers(self) -> None:
        """Fetch and parse ProtonVPN server data."""
        try:
            response = requests.get(self.data_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.servers = data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ProtonVPN server data: {e}")

    def get_p2p_servers(self) -> List[Dict]:
        """Get list of P2P-enabled servers.

        Returns:
            List of server dictionaries with P2P support
        """
        if not self.servers:
            self.fetch_servers()

        p2p_servers = []
        for server in self.servers:
            if server.get("P2P Feature Enabled", False):
                p2p_servers.append(
                    {
                        "name": server.get("Name", ""),
                        "country": server.get("Country", ""),
                        "city": server.get("City", ""),
                        "lat": server.get("Latitude"),
                        "lon": server.get("Longitude"),
                        "load": server.get("Load", 0),
                        "status": server.get("Status", 1),
                    }
                )

        return p2p_servers

    def load_from_file(self, filepath: str) -> None:
        """Load server data from local JSON file.

        Args:
            filepath: Path to local JSON file
        """
        try:
            with open(filepath, "r") as f:
                self.servers = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load server data from file: {e}")
