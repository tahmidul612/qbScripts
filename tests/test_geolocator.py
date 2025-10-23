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


def test_geolocate_failure(geolocator):
    """Test handling of API failure."""
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
