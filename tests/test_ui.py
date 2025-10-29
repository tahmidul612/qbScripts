"""Tests for ui module."""

import pytest
from qb_peer_vpn.ui import TerminalUI


@pytest.fixture
def ui():
    """Create UI instance."""
    return TerminalUI()


@pytest.fixture
def sample_recommendations():
    """Create sample recommendation data."""
    return [
        {
            "cluster": {
                "peer_count": 50,
                "city": "London",
                "country": "United Kingdom",
            },
            "server": {
                "name": "UK-LON#1",
                "city": "London",
                "country": "United Kingdom",
                "distance_to_cluster": 5.2,
                "load": 45,
            },
            "score": 0.1,
        },
        {
            "cluster": {
                "peer_count": 30,
                "city": "New York",
                "country": "United States",
            },
            "server": {
                "name": "US-NY#1",
                "city": "New York",
                "country": "United States",
                "distance_to_cluster": 2.1,
                "load": 38,
            },
            "score": 0.07,
        },
        {
            "cluster": {
                "peer_count": 15,
                "city": "Tokyo",
                "country": "Japan",
            },
            "server": {
                "name": "JP-TOK#1",
                "city": "Tokyo",
                "country": "Japan",
                "distance_to_cluster": 0.5,
                "load": 52,
            },
            "score": 0.033,
        },
    ]


@pytest.fixture
def user_location():
    """Create user location data."""
    return {
        "lat": 37.7749,
        "lon": -122.4194,
        "city": "San Francisco",
        "country": "United States",
    }


def test_display_summary(ui, capsys):
    """Test summary display."""
    ui.display_summary(total_peers=100, total_ips=10, clusters=3)
    captured = capsys.readouterr()

    assert "Analysis Summary" in captured.out
    assert "100" in captured.out
    assert "10" in captured.out
    assert "3" in captured.out
    assert "peer concentration area" in captured.out


def test_display_recommendations_without_user_location(
    ui, sample_recommendations, capsys
):
    """Test recommendations display without user location."""
    ui.display_recommendations(sample_recommendations, user_location=None)
    captured = capsys.readouterr()

    assert "Optimal VPN Server Recommendations" in captured.out
    assert "Better Torrent Performance" in captured.out
    assert "Why these recommendations matter" in captured.out
    assert "Best Overall Choice" in captured.out
    assert "UK-LON#1" in captured.out  # Largest cluster
    assert "Priority" in captured.out
    assert "Peer Cluster Location" in captured.out


def test_display_recommendations_with_user_location(
    ui, sample_recommendations, user_location, capsys
):
    """Test recommendations display with user location."""
    ui.display_recommendations(sample_recommendations, user_location)
    captured = capsys.readouterr()

    assert "Your Current Location" in captured.out
    assert "San Francisco" in captured.out
    assert "United States" in captured.out


def test_display_recommendations_sorting(ui, sample_recommendations, capsys):
    """Test that recommendations are sorted by peer count."""
    ui.display_recommendations(sample_recommendations, user_location=None)
    captured = capsys.readouterr()

    # Check that UK-LON#1 (50 peers) appears before US-NY#1 (30 peers)
    uk_pos = captured.out.find("UK-LON#1")
    us_pos = captured.out.find("US-NY#1")
    assert uk_pos < us_pos
    assert "★" in captured.out  # Priority marker


def test_display_recommendations_distance_formatting(
    ui, sample_recommendations, capsys
):
    """Test distance formatting in recommendations."""
    ui.display_recommendations(sample_recommendations, user_location=None)
    captured = capsys.readouterr()

    # Check for km units
    assert "km" in captured.out
    # For small distances (<1 km), should show meters
    small_distance_rec = [
        {
            "cluster": {"peer_count": 10, "city": "Test", "country": "Test"},
            "server": {
                "name": "TEST#1",
                "city": "Test",
                "country": "Test",
                "distance_to_cluster": 0.5,
            },
            "score": 0.05,
        }
    ]
    ui.display_recommendations(small_distance_rec, user_location=None)
    captured = capsys.readouterr()
    assert "m" in captured.out  # meters for < 1 km


def test_display_error(ui, capsys):
    """Test error message display."""
    ui.display_error("Test error message")
    captured = capsys.readouterr()

    assert "Error" in captured.out
    assert "Test error message" in captured.out


def test_display_warning(ui, capsys):
    """Test warning message display."""
    ui.display_warning("Test warning message")
    captured = capsys.readouterr()

    assert "Warning" in captured.out
    assert "Test warning message" in captured.out


def test_display_info(ui, capsys):
    """Test info message display."""
    ui.display_info("Test info message")
    captured = capsys.readouterr()

    assert "Info" in captured.out
    assert "Test info message" in captured.out
