"""Tests for geolocator module."""

import pytest
from unittest.mock import patch, Mock
from qb_peer_vpn.geolocator import IPGeolocator


@pytest.fixture
def geolocator():
    """Create geolocator instance."""
    return IPGeolocator(cache_ttl=60, max_cache_size=10)


def test_geolocate_success(geolocator):
    """Test successful IP geolocation."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "success",
        "lat": 40.7128,
        "lon": -74.0060,
        "country": "United States",
        "city": "New York",
    }

    with patch("requests.get", return_value=mock_response):
        result = geolocator.geolocate("8.8.8.8")

    assert result["lat"] == 40.7128
    assert result["lon"] == -74.0060
    assert result["country"] == "United States"
    assert result["city"] == "New York"


def test_geolocate_caching(geolocator):
    """Test that geolocation results are cached."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "success",
        "lat": 40.7128,
        "lon": -74.0060,
        "country": "United States",
        "city": "New York",
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        # First call
        result1 = geolocator.geolocate("8.8.8.8")
        # Second call should use cache
        result2 = geolocator.geolocate("8.8.8.8")

        assert result1 == result2
        # Should only call API once
        assert mock_get.call_count == 1


def test_geolocate_failure_with_fallback(geolocator):
    """Test fallback to alternative providers on primary failure."""
    # Mock primary provider to fail
    mock_primary = Mock()
    mock_primary.json.return_value = {"status": "fail"}

    # Mock fallback provider (ipapi.co) to succeed
    mock_fallback = Mock()
    mock_fallback.json.return_value = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "country_name": "United States",
        "city": "San Francisco",
    }

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [mock_primary, mock_fallback]
        result = geolocator.geolocate("8.8.8.8")

    assert result is not None
    assert result["lat"] == 37.7749
    assert result["lon"] == -122.4194
    assert result["country"] == "United States"
    assert result["city"] == "San Francisco"


def test_geolocate_failure(geolocator):
    """Test handling of complete API failure."""
    with patch("requests.get", side_effect=Exception("API Error")):
        result = geolocator.geolocate("8.8.8.8")

    assert result is None


def test_get_current_location(geolocator):
    """Test getting current location."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": "success",
        "query": "1.2.3.4",
        "lat": 51.5074,
        "lon": -0.1278,
        "country": "United Kingdom",
        "city": "London",
    }

    with patch("requests.get", return_value=mock_response):
        result = geolocator.get_current_location()

    assert result["ip"] == "1.2.3.4"
    assert result["city"] == "London"


def test_get_current_location_fallback(geolocator):
    """Test fallback for current location."""
    # Mock primary to fail
    mock_primary = Mock()
    mock_primary.json.return_value = {"status": "fail"}

    # Mock fallback to succeed
    mock_fallback = Mock()
    mock_fallback.json.return_value = {
        "ip": "5.6.7.8",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "country_name": "France",
        "city": "Paris",
    }

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [mock_primary, mock_fallback]
        result = geolocator.get_current_location()

    assert result is not None
    assert result["ip"] == "5.6.7.8"
    assert result["city"] == "Paris"


def test_geolocate_batch_success(geolocator):
    """Test batch geolocation with successful batch request."""
    ips = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]

    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "status": "success",
            "query": "8.8.8.8",
            "lat": 37.7749,
            "lon": -122.4194,
            "country": "United States",
            "city": "San Francisco",
        },
        {
            "status": "success",
            "query": "1.1.1.1",
            "lat": -33.8688,
            "lon": 151.2093,
            "country": "Australia",
            "city": "Sydney",
        },
        {
            "status": "success",
            "query": "9.9.9.9",
            "lat": 51.5074,
            "lon": -0.1278,
            "country": "United Kingdom",
            "city": "London",
        },
    ]

    with patch("requests.post", return_value=mock_response):
        results = geolocator.geolocate_batch(ips)

    assert len(results) == 3
    assert results["8.8.8.8"]["city"] == "San Francisco"
    assert results["1.1.1.1"]["city"] == "Sydney"
    assert results["9.9.9.9"]["city"] == "London"


def test_geolocate_batch_with_cached_ips(geolocator):
    """Test batch geolocation with some cached IPs."""
    # Add one IP to cache
    geolocator.cache["8.8.8.8"] = {
        "lat": 37.7749,
        "lon": -122.4194,
        "country": "United States",
        "city": "San Francisco",
    }

    ips = ["8.8.8.8", "1.1.1.1"]

    # Only uncached IP should be requested
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "status": "success",
            "query": "1.1.1.1",
            "lat": -33.8688,
            "lon": 151.2093,
            "country": "Australia",
            "city": "Sydney",
        }
    ]

    with patch("requests.post", return_value=mock_response) as mock_post:
        results = geolocator.geolocate_batch(ips)

    assert len(results) == 2
    assert results["8.8.8.8"]["city"] == "San Francisco"
    assert results["1.1.1.1"]["city"] == "Sydney"
    # Batch request should only be called once for uncached IP
    assert mock_post.call_count == 1


def test_geolocate_batch_with_progress_callback(geolocator):
    """Test batch geolocation with progress callback."""
    ips = ["8.8.8.8", "1.1.1.1"]
    progress_calls = []

    def progress_callback(current, total, ip):
        progress_calls.append((current, total, ip))

    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "status": "success",
            "query": "8.8.8.8",
            "lat": 37.7749,
            "lon": -122.4194,
            "country": "United States",
            "city": "San Francisco",
        },
        {
            "status": "success",
            "query": "1.1.1.1",
            "lat": -33.8688,
            "lon": 151.2093,
            "country": "Australia",
            "city": "Sydney",
        },
    ]

    with patch("requests.post", return_value=mock_response):
        geolocator.geolocate_batch(ips, progress_callback=progress_callback)

    # Progress callback should be called for each IP
    assert len(progress_calls) >= 2


def test_geolocate_batch_splits_large_lists(geolocator):
    """Test that batch geolocation splits lists larger than 100."""
    # Create 150 IPs
    ips = [f"1.2.3.{i}" for i in range(150)]

    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "status": "success",
            "query": ip,
            "lat": 37.7749,
            "lon": -122.4194,
            "country": "United States",
            "city": "San Francisco",
        }
        for ip in ips[:100]  # First batch of 100
    ]

    mock_response2 = Mock()
    mock_response2.json.return_value = [
        {
            "status": "success",
            "query": ip,
            "lat": 37.7749,
            "lon": -122.4194,
            "country": "United States",
            "city": "San Francisco",
        }
        for ip in ips[100:]  # Second batch of 50
    ]

    with patch("requests.post") as mock_post:
        mock_post.side_effect = [mock_response, mock_response2]
        results = geolocator.geolocate_batch(ips)

    # Should make 2 batch requests (100 + 50)
    assert mock_post.call_count == 2
    assert len(results) == 150
