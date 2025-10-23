"""Tests for peer_fetcher module."""

import pytest
from unittest.mock import Mock, patch
from qb_peer_vpn.peer_fetcher import QBitPeerFetcher


@pytest.fixture
def mock_client():
    """Create a mock qBittorrent client."""
    with patch("qb_peer_vpn.peer_fetcher.qbittorrentapi.Client") as mock:
        yield mock


def test_connection_success(mock_client):
    """Test successful connection to qBittorrent."""
    fetcher = QBitPeerFetcher("localhost", 8080, "admin", "password")
    fetcher.connect()
    fetcher.client.auth_log_in.assert_called_once()


def test_get_all_peers_empty(mock_client):
    """Test fetching peers when no torrents exist."""
    fetcher = QBitPeerFetcher("localhost", 8080, "admin", "password")
    fetcher.client.torrents_info.return_value = []

    peers = fetcher.get_all_peers()
    assert peers == {}


def test_get_all_peers_with_data(mock_client):
    """Test fetching peers with mock data."""
    fetcher = QBitPeerFetcher("localhost", 8080, "admin", "password")

    # Mock torrent
    mock_torrent = Mock()
    mock_torrent.hash = "test_hash"
    mock_torrent.name = "Test Torrent"
    fetcher.client.torrents_info.return_value = [mock_torrent]

    # Mock peers
    mock_peers = Mock()
    mock_peers.peers = {
        "peer1": {"ip": "1.2.3.4"},
        "peer2": {"ip": "5.6.7.8"},
        "peer3": {"ip": "1.2.3.4"},  # Duplicate IP
    }
    fetcher.client.sync_torrent_peers.return_value = mock_peers

    peers = fetcher.get_all_peers()
    assert peers == {"1.2.3.4": 2, "5.6.7.8": 1}
