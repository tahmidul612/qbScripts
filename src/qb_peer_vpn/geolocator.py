"""Module for IP geolocation with caching and fallback."""

from typing import Optional, Dict
import requests
from cachetools import TTLCache
import time


class IPGeolocator:
    """Geolocate IP addresses with caching and provider fallback."""

    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 1000):
        """Initialize geolocator with cache.

        Args:
            cache_ttl: Time-to-live for cache entries in seconds
            max_cache_size: Maximum number of cached entries
        """
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)
        self.primary_url = "http://ip-api.com/json/{}"
        self.last_request_time = 0
        self.min_request_interval = 1.4  # Rate limit: ~45 req/min

    def _rate_limit(self) -> None:
        """Enforce rate limiting for API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def geolocate(self, ip: str) -> Optional[Dict[str, any]]:
        """Get geolocation data for an IP address.

        Args:
            ip: IP address to geolocate

        Returns:
            Dictionary with keys: lat, lon, country, city, or None if failed
        """
        if ip in self.cache:
            return self.cache[ip]

        self._rate_limit()

        try:
            response = requests.get(self.primary_url.format(ip), timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                result = {
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "country": data.get("country"),
                    "city": data.get("city"),
                }
                self.cache[ip] = result
                return result
        except Exception as e:
            print(f"Warning: Failed to geolocate IP {ip}: {e}")

        return None

    def get_current_location(self) -> Optional[Dict[str, any]]:
        """Get current public IP and location.

        Returns:
            Dictionary with location data including current IP
        """
        try:
            response = requests.get("http://ip-api.com/json/", timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success":
                return {
                    "ip": data.get("query"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "country": data.get("country"),
                    "city": data.get("city"),
                }
        except Exception as e:
            print(f"Warning: Failed to get current location: {e}")

        return None

    def geolocate_batch(self, ips: list) -> Dict[str, Optional[Dict]]:
        """Geolocate multiple IP addresses.

        Args:
            ips: List of IP addresses

        Returns:
            Dictionary mapping IP to geolocation data
        """
        results = {}
        for ip in ips:
            results[ip] = self.geolocate(ip)
        return results
