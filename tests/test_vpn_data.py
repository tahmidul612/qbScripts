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
    mock_response.json.return_value = {
        "genDate": "2025-10-08T06:37:17.311Z",
        "data": [
            {
                "ipv4": "1.2.3.4",
                "ipv6": None,
                "domain": "us-01.protonvpn.net",
                "servers": ["US#1", "US#2"],
                "ipv6Enabled": False,
                "city": "New York",
                "P2P": True,
                "Streaming": True,
            }
        ],
    }

    with patch("requests.get", return_value=mock_response):
        vpn_data.fetch_servers()

    assert len(vpn_data.servers) == 1
    assert vpn_data.servers[0]["city"] == "New York"


def test_get_p2p_servers(vpn_data):
    """Test filtering P2P-enabled servers."""
    vpn_data.servers = [
        {
            "ipv4": "1.2.3.4",
            "domain": "us-01.protonvpn.net",
            "servers": ["US#1", "US#2"],
            "city": "New York",
            "P2P": True,
            "Streaming": True,
        },
        {
            "ipv4": "5.6.7.8",
            "domain": "fr-01.protonvpn.net",
            "servers": ["FR#1"],
            "city": "Paris",
            "P2P": False,
            "Streaming": True,
        },
        {
            "ipv4": "9.10.11.12",
            "domain": "nl-01.protonvpn.net",
            "servers": ["NL#1", "NL#2", "NL#3"],
            "city": "Amsterdam",
            "P2P": True,
            "Streaming": False,
        },
    ]

    # Test without geocoding to avoid external API calls
    p2p_servers = vpn_data.get_p2p_servers(geocode=False)

    assert len(p2p_servers) == 2
    assert all(s["country"] in ["US", "NL"] for s in p2p_servers)
    assert p2p_servers[0]["city"] == "New York"
    assert p2p_servers[1]["city"] == "Amsterdam"
