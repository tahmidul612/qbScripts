"""Module for IP geolocation with caching and fallback."""

from typing import Optional, Dict
import requests
from cachetools import TTLCache
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        self.batch_url = "http://ip-api.com/batch"
        self.last_request_time = 0
        self.min_request_interval = 1.4  # Rate limit: ~45 req/min
        self.batch_rate_limit = 4.0  # 15 req/min = 1 req per 4 seconds
        self.last_batch_request_time = 0

        # Fallback providers
        self.fallback_providers = [
            self._geolocate_ipapi_co,
            self._geolocate_freeipapi,
        ]

    def _rate_limit(self) -> None:
        """Enforce rate limiting for API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _batch_rate_limit(self) -> None:
        """Enforce rate limiting for batch API requests."""
        elapsed = time.time() - self.last_batch_request_time
        if elapsed < self.batch_rate_limit:
            time.sleep(self.batch_rate_limit - elapsed)
        self.last_batch_request_time = time.time()

    def _geolocate_ipapi_co(self, ip: str) -> Optional[Dict[str, any]]:
        """Fallback geolocation using ipapi.co.

        Args:
            ip: IP address to geolocate

        Returns:
            Dictionary with location data or None if failed
        """
        try:
            response = requests.get(
                f"https://ipapi.co/{ip}/json/",
                timeout=5,
                headers={"User-Agent": "qb-peer-vpn/0.2.0"},
            )
            response.raise_for_status()
            data = response.json()

            if "error" not in data:
                return {
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                    "country": data.get("country_name"),
                    "city": data.get("city"),
                }
        except Exception:
            pass
        return None

    def _geolocate_freeipapi(self, ip: str) -> Optional[Dict[str, any]]:
        """Fallback geolocation using freeipapi.com.

        Args:
            ip: IP address to geolocate

        Returns:
            Dictionary with location data or None if failed
        """
        try:
            response = requests.get(
                f"https://freeipapi.com/api/json/{ip}",
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("latitude") is not None and data.get("longitude") is not None:
                return {
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                    "country": data.get("countryName"),
                    "city": data.get("cityName"),
                }
        except Exception:
            pass
        return None

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

        # Try primary provider
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
        except Exception:
            pass

        # Try fallback providers
        for fallback in self.fallback_providers:
            try:
                result = fallback(ip)
                if result:
                    self.cache[ip] = result
                    return result
            except Exception:
                continue

        return None

    def _geolocate_batch_request(
        self, ips: list[str]
    ) -> Dict[str, Optional[Dict[str, any]]]:
        """Make a batch geolocation request.

        Args:
            ips: List of up to 100 IP addresses

        Returns:
            Dictionary mapping IP to geolocation data
        """
        results = {}

        self._batch_rate_limit()

        try:
            # IP-API.com batch endpoint accepts up to 100 IPs
            response = requests.post(
                self.batch_url,
                json=ips,
                timeout=10,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            for item in data:
                if item.get("status") == "success":
                    ip = item.get("query")
                    result = {
                        "lat": item.get("lat"),
                        "lon": item.get("lon"),
                        "country": item.get("country"),
                        "city": item.get("city"),
                    }
                    results[ip] = result
                    self.cache[ip] = result
                else:
                    results[item.get("query")] = None

        except Exception:
            # If batch fails, mark all as None and they'll be retried individually
            for ip in ips:
                results[ip] = None

        return results

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
        except Exception:
            pass

        # Try fallback for current location
        try:
            response = requests.get(
                "https://ipapi.co/json/",
                timeout=5,
                headers={"User-Agent": "qb-peer-vpn/0.2.0"},
            )
            response.raise_for_status()
            data = response.json()

            if "error" not in data:
                return {
                    "ip": data.get("ip"),
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                    "country": data.get("country_name"),
                    "city": data.get("city"),
                }
        except Exception:
            pass

        return None

    def geolocate_batch(
        self, ips: list[str], progress_callback=None
    ) -> Dict[str, Optional[Dict]]:
        """Geolocate multiple IP addresses using batch requests and parallel processing.

        Args:
            ips: List of IP addresses
            progress_callback: Optional callback function(current, total, ip) for progress

        Returns:
            Dictionary mapping IP to geolocation data
        """
        results = {}

        # Filter out cached IPs
        uncached_ips = [ip for ip in ips if ip not in self.cache]

        # Get cached results
        for ip in ips:
            if ip in self.cache:
                results[ip] = self.cache[ip]
                if progress_callback:
                    progress_callback(len(results), len(ips), ip)

        if not uncached_ips:
            return results

        # Split into batches of 100 (IP-API.com limit)
        batch_size = 100
        batches = [
            uncached_ips[i : i + batch_size]
            for i in range(0, len(uncached_ips), batch_size)
        ]

        # Process batches sequentially (rate limited to 15 req/min)
        for batch in batches:
            batch_results = self._geolocate_batch_request(batch)

            # Retry failed IPs from batch individually with fallback
            failed_ips = [ip for ip, result in batch_results.items() if result is None]

            if failed_ips:
                # Use thread pool for parallel fallback requests
                with ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_ip = {
                        executor.submit(self.geolocate, ip): ip for ip in failed_ips
                    }

                    for future in as_completed(future_to_ip):
                        ip = future_to_ip[future]
                        try:
                            result = future.result()
                            batch_results[ip] = result
                        except Exception:
                            batch_results[ip] = None

            results.update(batch_results)

            # Update progress
            if progress_callback:
                for ip in batch:
                    progress_callback(len(results), len(ips), ip)

        return results
