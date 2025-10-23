"""Tests for cluster_analyzer module."""

import pytest
from qb_peer_vpn.cluster_analyzer import PeerClusterAnalyzer


@pytest.fixture
def analyzer():
    """Create analyzer instance."""
    return PeerClusterAnalyzer(n_clusters=2)


@pytest.fixture
def sample_peer_locations():
    """Create sample peer location data."""
    return {
        "1.2.3.4": {
            "lat": 40.7128,
            "lon": -74.0060,
            "count": 5,
            "country": "US",
            "city": "NYC",
        },
        "5.6.7.8": {
            "lat": 40.7580,
            "lon": -73.9855,
            "count": 3,
            "country": "US",
            "city": "NYC",
        },
        "9.10.11.12": {
            "lat": 51.5074,
            "lon": -0.1278,
            "count": 8,
            "country": "UK",
            "city": "London",
        },
    }


def test_cluster_peers_empty(analyzer):
    """Test clustering with no peers."""
    clusters = analyzer.cluster_peers({})
    assert clusters == []


def test_cluster_peers_single(analyzer):
    """Test clustering with single location."""
    locations = {
        "1.2.3.4": {
            "lat": 40.7128,
            "lon": -74.0060,
            "count": 5,
            "country": "US",
            "city": "NYC",
        }
    }

    clusters = analyzer.cluster_peers(locations)
    assert len(clusters) == 1
    assert clusters[0]["peer_count"] == 5


def test_cluster_peers_multiple(analyzer, sample_peer_locations):
    """Test clustering with multiple locations."""
    clusters = analyzer.cluster_peers(sample_peer_locations)

    assert len(clusters) == 2
    assert sum(c["peer_count"] for c in clusters) == 16  # 5 + 3 + 8


def test_get_overall_centroid(analyzer, sample_peer_locations):
    """Test calculating overall centroid."""
    centroid = analyzer.get_overall_centroid(sample_peer_locations)

    assert centroid is not None
    assert isinstance(centroid, tuple)
    assert len(centroid) == 2


def test_recommend_servers(analyzer, sample_peer_locations):
    """Test server recommendations."""
    clusters = analyzer.cluster_peers(sample_peer_locations)

    vpn_servers = [
        {
            "name": "US-NY#1",
            "country": "US",
            "city": "NYC",
            "lat": 40.7128,
            "lon": -74.0060,
            "load": 45,
        },
        {
            "name": "UK-LON#1",
            "country": "UK",
            "city": "London",
            "lat": 51.5074,
            "lon": -0.1278,
            "load": 30,
        },
    ]

    recommendations = analyzer.recommend_servers(clusters, vpn_servers)

    assert len(recommendations) == len(clusters)
    assert all("cluster" in rec and "server" in rec for rec in recommendations)
