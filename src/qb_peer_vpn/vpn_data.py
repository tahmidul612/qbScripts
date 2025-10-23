"""Module for ProtonVPN server data management."""

from typing import List, Dict, Optional
import requests
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time


class ProtonVPNData:
    """Manage ProtonVPN server data."""

    def __init__(self, data_url: Optional[str] = None):
        """Initialize with ProtonVPN data source.

        Args:
            data_url: URL to ProtonVPN server JSON data
        """
        self.data_url = data_url or (
            "https://raw.githubusercontent.com/huzky-v/proton-vpn-server-list/refs/heads/main/output-group/all.json"
        )
        self.servers = []
        self.geolocator = Nominatim(user_agent="qb-peer-vpn")
        self._geocode_cache = {}

    def fetch_servers(self) -> None:
        """Fetch and parse ProtonVPN server data."""
        try:
            response = requests.get(self.data_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # New format has data wrapped in 'data' key
            if isinstance(data, dict) and "data" in data:
                self.servers = data["data"]
            else:
                self.servers = data
        except Exception as e:
            raise RuntimeError(f"Failed to fetch ProtonVPN server data: {e}")

    def _geocode_city(self, city: str, country_code: str) -> Optional[tuple]:
        """Geocode a city to get lat/lon coordinates.

        Args:
            city: City name
            country_code: 2-letter country code

        Returns:
            Tuple of (latitude, longitude) or None
        """
        cache_key = f"{city},{country_code}"
        if cache_key in self._geocode_cache:
            return self._geocode_cache[cache_key]

        try:
            location = self.geolocator.geocode(f"{city}, {country_code}", timeout=5)
            if location:
                result = (location.latitude, location.longitude)
                self._geocode_cache[cache_key] = result
                time.sleep(1)  # Rate limiting for Nominatim
                return result
        except (GeocoderTimedOut, GeocoderServiceError):
            pass

        self._geocode_cache[cache_key] = None
        return None

    def get_p2p_servers(self, geocode: bool = True) -> List[Dict]:
        """Get list of P2P-enabled servers.

        Args:
            geocode: Whether to geocode city locations (default: True)

        Returns:
            List of server dictionaries with P2P support
        """
        if not self.servers:
            self.fetch_servers()

        p2p_servers = []
        for server in self.servers:
            if server.get("P2P", False):
                # Extract country from server names (e.g., "US#1" -> "US")
                server_names = server.get("servers", [])
                country_code = (
                    server_names[0].split("#")[0] if server_names else "Unknown"
                )

                # Get location from city
                city = server.get("city", "Unknown")

                # Geocode city to get lat/lon if requested
                lat, lon = None, None
                if geocode and city != "Unknown" and country_code != "Unknown":
                    coords = self._geocode_city(city, country_code)
                    if coords:
                        lat, lon = coords

                p2p_servers.append(
                    {
                        "name": ", ".join(server_names[:3])
                        if len(server_names) <= 3
                        else f"{', '.join(server_names[:2])}... (+{len(server_names) - 2})",
                        "servers": server_names,
                        "country": country_code,
                        "city": city,
                        "lat": lat,
                        "lon": lon,
                        "ipv4": server.get("ipv4"),
                        "ipv6": server.get("ipv6"),
                        "load": 0,  # Not provided in this API
                        "status": 1,
                        "streaming": server.get("Streaming", False),
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
