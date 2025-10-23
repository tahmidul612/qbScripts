"""Tests for vpn_data module."""

import pytest
from unittest.mock import patch, Mock
from qb_peer_vpn.vpn_data import ProtonVPNData


@pytest.fixture
def vpn_data():
    """Create VPN data instance."""
    return ProtonVPNData()


def test_fetch_servers(vpn_data):
    """Test fetching server data from API."""
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "Name": "US-NY#1",
            "Country": "United States",
            "City": "New York",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "P2P Feature Enabled": True,
            "Load": 45,
            "Status": 1,
        }
    ]

    with patch("requests.get", return_value=mock_response):
        vpn_data.fetch_servers()

    assert len(vpn_data.servers) == 1
    assert vpn_data.servers[0]["Name"] == "US-NY#1"


def test_get_p2p_servers(vpn_data):
    """Test filtering P2P-enabled servers."""
    vpn_data.servers = [
        {
            "Name": "US-NY#1",
            "Country": "United States",
            "City": "New York",
            "Latitude": 40.7128,
            "Longitude": -74.0060,
            "P2P Feature Enabled": True,
            "Load": 45,
            "Status": 1,
        },
        {
            "Name": "FR-PAR#1",
            "Country": "France",
            "City": "Paris",
            "Latitude": 48.8566,
            "Longitude": 2.3522,
            "P2P Feature Enabled": False,
            "Load": 30,
            "Status": 1,
        },
        {
            "Name": "NL-AMS#1",
            "Country": "Netherlands",
            "City": "Amsterdam",
            "Latitude": 52.3676,
            "Longitude": 4.9041,
            "P2P Feature Enabled": True,
            "Load": 20,
            "Status": 1,
        },
    ]

    p2p_servers = vpn_data.get_p2p_servers()

    assert len(p2p_servers) == 2
    assert all(s["name"] in ["US-NY#1", "NL-AMS#1"] for s in p2p_servers)
