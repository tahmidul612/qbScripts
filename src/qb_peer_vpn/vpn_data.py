"""Module for ProtonVPN server data management."""

from typing import List, Dict, Optional
import requests
import json
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError


# Static coordinates for common ProtonVPN cities (lat, lon) - used as fallback
CITY_COORDINATES_FALLBACK = {
    ("Amsterdam", "NL"): (52.3676, 4.9041),
    ("Frankfurt", "DE"): (50.1109, 8.6821),
    ("Zurich", "CH"): (47.3769, 8.5417),
    ("London", "UK"): (51.5074, -0.1278),
    ("Paris", "FR"): (48.8566, 2.3522),
    ("Stockholm", "SE"): (59.3293, 18.0686),
    ("Copenhagen", "DK"): (55.6761, 12.5683),
    ("Oslo", "NO"): (59.9139, 10.7522),
    ("Helsinki", "FI"): (60.1699, 24.9384),
    ("Warsaw", "PL"): (52.2297, 21.0122),
    ("Prague", "CZ"): (50.0755, 14.4378),
    ("Vienna", "AT"): (48.2082, 16.3738),
    ("Brussels", "BE"): (50.8503, 4.3517),
    ("Madrid", "ES"): (40.4168, -3.7038),
    ("Barcelona", "ES"): (41.3851, 2.1734),
    ("Rome", "IT"): (41.9028, 12.4964),
    ("Milan", "IT"): (45.4642, 9.1900),
    ("Lisbon", "PT"): (38.7223, -9.1393),
    ("Dublin", "IE"): (53.3498, -6.2603),
    ("Athens", "GR"): (37.9838, 23.7275),
    ("Budapest", "HU"): (47.4979, 19.0402),
    ("Bucharest", "RO"): (44.4268, 26.1025),
    ("Sofia", "BG"): (42.6977, 23.3219),
    ("Belgrade", "RS"): (44.7866, 20.4489),
    ("Zagreb", "HR"): (45.8150, 15.9819),
    ("Vilnius", "LT"): (54.6872, 25.2797),
    ("Riga", "LV"): (56.9496, 24.1052),
    ("Tallinn", "EE"): (59.4370, 24.7536),
    ("Reykjavik", "IS"): (64.1466, -21.9426),
    ("New York", "US-NY"): (40.7128, -74.0060),
    ("Los Angeles", "US-CA"): (34.0522, -118.2437),
    ("Chicago", "US-IL"): (41.8781, -87.6298),
    ("San Francisco", "US-CA"): (37.7749, -122.4194),
    ("Seattle", "US-WA"): (47.6062, -122.3321),
    ("Miami", "US-FL"): (25.7617, -80.1918),
    ("Dallas", "US-TX"): (32.7767, -96.7970),
    ("Atlanta", "US-GA"): (33.7490, -84.3880),
    ("Denver", "US-CO"): (39.7392, -104.9903),
    ("Phoenix", "US-AZ"): (33.4484, -112.0740),
    ("Boston", "US-MA"): (42.3601, -71.0589),
    ("Washington", "US-DC"): (38.9072, -77.0369),
    ("Ashburn", "US-VA"): (39.0438, -77.4874),
    ("Toronto", "CA-ON"): (43.6532, -79.3832),
    ("Montreal", "CA-QC"): (45.5017, -73.5673),
    ("Vancouver", "CA-BC"): (49.2827, -123.1207),
    ("Sydney", "AU"): (-33.8688, 151.2093),
    ("Melbourne", "AU"): (-37.8136, 144.9631),
    ("Brisbane", "AU"): (-27.4698, 153.0251),
    ("Perth", "AU"): (-31.9505, 115.8605),
    ("Adelaide", "AU"): (-34.9285, 138.6007),
    ("Auckland", "NZ"): (-36.8485, 174.7633),
    ("Tokyo", "JP"): (35.6762, 139.6503),
    ("Singapore", "SG"): (1.3521, 103.8198),
    ("Hong Kong", "HK"): (22.3193, 114.1694),
    ("Seoul", "KR"): (37.5665, 126.9780),
    ("Taipei", "TW"): (25.0330, 121.5654),
    ("Bangkok", "TH"): (13.7563, 100.5018),
    ("Mumbai", "IN"): (19.0760, 72.8777),
    ("Delhi", "IN"): (28.6139, 77.2090),
    ("Bangalore", "IN"): (12.9716, 77.5946),
    ("Dubai", "AE"): (25.2048, 55.2708),
    ("Tel Aviv", "IL"): (32.0853, 34.7818),
    ("Istanbul", "TR"): (41.0082, 28.9784),
    ("Cairo", "EG"): (30.0444, 31.2357),
    ("Johannesburg", "ZA"): (-26.2041, 28.0473),
    ("Cape Town", "ZA"): (-33.9249, 18.4241),
    ("Sao Paulo", "BR"): (-23.5505, -46.6333),
    ("Rio de Janeiro", "BR"): (-22.9068, -43.1729),
    ("Buenos Aires", "AR"): (-34.6037, -58.3816),
    ("Mexico City", "MX"): (19.4326, -99.1332),
    ("Santiago", "CL"): (-33.4489, -70.6693),
    ("Lima", "PE"): (-12.0464, -77.0428),
    ("Bogota", "CO"): (4.7110, -74.0721),
    ("Caracas", "VE"): (10.4806, -66.9036),
    ("Belfast", "UK"): (54.5973, -5.9301),
    ("Edinburgh", "UK"): (55.9533, -3.1883),
    ("Manchester", "UK"): (53.4808, -2.2426),
}


class ProtonVPNData:
    """Manage ProtonVPN server data."""

    def __init__(self, data_url: Optional[str] = None, geocode_cache_ttl: int = 86400):
        """Initialize with ProtonVPN data source.

        Args:
            data_url: URL to ProtonVPN server JSON data
            geocode_cache_ttl: Cache TTL for geocoding in seconds (default: 24 hours)
        """
        self.data_url = data_url or (
            "https://raw.githubusercontent.com/huzky-v/proton-vpn-server-list/refs/heads/main/output-group/all.json"
        )
        self.servers = []
        # Long TTL cache for city geocoding (24 hours default)
        self.geocode_cache = TTLCache(maxsize=500, ttl=geocode_cache_ttl)

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

    def _geocode_nominatim(self, city: str, country_code: str) -> Optional[tuple]:
        """Geocode using Nominatim (OpenStreetMap).

        Args:
            city: City name
            country_code: Country code

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Nominatim requires a user agent
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": f"{city}, {country_code}",
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "qb-peer-vpn/0.2.0"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
        except Exception:
            pass
        return None

    def _geocode_geocodeapi(self, city: str, country_code: str) -> Optional[tuple]:
        """Geocode using geocode.maps.co (fallback).

        Args:
            city: City name
            country_code: Country code

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            response = requests.get(
                "https://geocode.maps.co/search",
                params={
                    "q": f"{city}, {country_code}",
                    "format": "json",
                },
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
        except Exception:
            pass
        return None

    def _geocode_city(self, city: str, country_code: str) -> Optional[tuple]:
        """Geocode a city using multiple providers with fallback.

        Args:
            city: City name
            country_code: Country code

        Returns:
            Tuple of (latitude, longitude) or None
        """
        cache_key = f"{city},{country_code}"

        # Check cache first
        if cache_key in self.geocode_cache:
            return self.geocode_cache[cache_key]

        # Check hardcoded fallback database first for common cities
        fallback_coords = CITY_COORDINATES_FALLBACK.get((city, country_code))

        # Try API providers in order with fallback
        providers = [
            self._geocode_nominatim,
            self._geocode_geocodeapi,
        ]

        for provider in providers:
            try:
                coords = provider(city, country_code)
                if coords:
                    self.geocode_cache[cache_key] = coords
                    return coords
            except Exception:
                continue

        # Use hardcoded fallback if API calls failed
        if fallback_coords:
            self.geocode_cache[cache_key] = fallback_coords
            return fallback_coords

        # Cache None to avoid repeated failed lookups
        self.geocode_cache[cache_key] = None
        return None

    def _geocode_cities_parallel(
        self, cities: List[tuple], timeout: float = 45.0
    ) -> Dict[tuple, Optional[tuple]]:
        """Geocode multiple cities in parallel with timeout.

        Args:
            cities: List of (city, country_code) tuples
            timeout: Maximum time in seconds to wait for all geocoding (default: 45)

        Returns:
            Dictionary mapping (city, country) to (lat, lon) or None
        """
        results = {}

        # Filter out cached cities
        uncached_cities = [
            c for c in cities if f"{c[0]},{c[1]}" not in self.geocode_cache
        ]

        # Get cached results
        for city, country in cities:
            cache_key = f"{city},{country}"
            if cache_key in self.geocode_cache:
                results[(city, country)] = self.geocode_cache[cache_key]

        if not uncached_cities:
            return results

        # Geocode uncached cities in parallel with timeout (max 5 concurrent)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_city = {
                executor.submit(self._geocode_city, city, country): (city, country)
                for city, country in uncached_cities
            }

            try:
                # Wait for all futures with timeout
                for future in as_completed(future_to_city, timeout=timeout):
                    city, country = future_to_city[future]
                    try:
                        coords = future.result(timeout=1)  # 1 second per result
                        results[(city, country)] = coords
                    except Exception:
                        # Use fallback for failed geocoding
                        fallback = CITY_COORDINATES_FALLBACK.get((city, country))
                        results[(city, country)] = fallback
                        if fallback:
                            self.geocode_cache[f"{city},{country}"] = fallback
            except TimeoutError:
                # Timeout reached - use fallback for remaining cities
                for future, (city, country) in future_to_city.items():
                    if (city, country) not in results:
                        fallback = CITY_COORDINATES_FALLBACK.get((city, country))
                        results[(city, country)] = fallback
                        if fallback:
                            self.geocode_cache[f"{city},{country}"] = fallback

        return results

    def get_p2p_servers(self, geocode: bool = True) -> List[Dict]:
        """Get list of P2P-enabled servers.

        Args:
            geocode: Whether to geocode city locations (default: True)
                    Uses parallel geocoding with fallback providers and 45s timeout

        Returns:
            List of server dictionaries with P2P support
        """
        if not self.servers:
            self.fetch_servers()

        # First pass: collect unique cities that need geocoding
        cities_to_geocode = set()
        for server in self.servers:
            if server.get("P2P", False):
                server_names = server.get("servers", [])
                country_code = (
                    server_names[0].split("#")[0] if server_names else "Unknown"
                )
                city = server.get("city", "Unknown")
                if geocode and city != "Unknown" and country_code != "Unknown":
                    cities_to_geocode.add((city, country_code))

        # Geocode all unique cities in parallel with 45s timeout
        city_coords = {}
        if cities_to_geocode:
            city_coords = self._geocode_cities_parallel(
                list(cities_to_geocode), timeout=45.0
            )

        # Second pass: build server list with coordinates
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

                # Get coordinates from geocoding results
                lat, lon = None, None
                if geocode and city != "Unknown" and country_code != "Unknown":
                    coords = city_coords.get((city, country_code))
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
