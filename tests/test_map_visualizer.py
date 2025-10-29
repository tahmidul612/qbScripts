"""Tests for map_visualizer module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from qb_peer_vpn.map_visualizer import MapVisualizer


@pytest.fixture
def visualizer():
    """Create visualizer instance."""
    return MapVisualizer(theme="light")


@pytest.fixture
def sample_clusters():
    """Create sample cluster data."""
    return [
        {
            "centroid": [40.7128, -74.0060],
            "peer_count": 10,
            "city": "New York",
            "country": "US",
        },
        {
            "centroid": [51.5074, -0.1278],
            "peer_count": 5,
            "city": "London",
            "country": "UK",
        },
    ]


@pytest.fixture
def sample_recommendations():
    """Create sample server recommendations."""
    return [
        {
            "server": {
                "name": "US-NY#1",
                "lat": 40.7128,
                "lon": -74.0060,
                "city": "New York",
                "country": "US",
                "load": 50,
                "distance_to_cluster": 10.5,
            },
            "cluster": {
                "centroid": [40.7128, -74.0060],
                "peer_count": 10,
                "city": "New York",
                "country": "US",
            },
        }
    ]


@pytest.fixture
def sample_user_location():
    """Create sample user location."""
    return {"lat": 40.7128, "lon": -74.0060, "city": "New York"}


def test_visualizer_initialization_light_theme():
    """Test visualizer initializes with light theme."""
    viz = MapVisualizer(theme="light")
    assert viz.theme == "light"
    assert viz.tile_layer == "CartoDB positron"


def test_visualizer_initialization_dark_theme():
    """Test visualizer initializes with dark theme."""
    viz = MapVisualizer(theme="dark")
    assert viz.theme == "dark"
    assert viz.tile_layer == "CartoDB dark_matter"


def test_create_map_generates_html(
    visualizer, sample_clusters, sample_recommendations, tmp_path
):
    """Test create_map generates HTML file."""
    output_file = tmp_path / "test_map.html"

    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert "leaflet" in content.lower() or "folium" in content.lower()


def test_create_map_with_user_location(
    visualizer, sample_clusters, sample_recommendations, sample_user_location, tmp_path
):
    """Test create_map includes user location."""
    output_file = tmp_path / "test_map_user.html"

    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        user_location=sample_user_location,
        output_file=str(output_file),
        render_png=False,
    )

    assert output_file.exists()


def test_create_map_with_empty_clusters(visualizer, sample_user_location, tmp_path):
    """Test create_map handles empty clusters."""
    output_file = tmp_path / "test_map_empty.html"

    visualizer.create_map(
        [],
        [],
        user_location=sample_user_location,
        output_file=str(output_file),
        render_png=False,
    )

    assert output_file.exists()


@patch("qb_peer_vpn.map_visualizer.subprocess.run")
def test_render_to_png_with_chrome_success(
    mock_run, visualizer, sample_clusters, sample_recommendations, tmp_path
):
    """Test PNG rendering succeeds with Chrome."""
    output_file = tmp_path / "test_map.html"
    png_file = tmp_path / "test_map.png"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock successful Chrome execution
    mock_run.return_value = Mock(returncode=0, stderr="")

    # Call render_to_png
    visualizer._render_to_png(str(output_file))

    # Verify subprocess.run was called with chrome
    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert "google-chrome" in call_args
    assert "--headless=new" in call_args
    assert f"--screenshot={png_file}" in call_args


@patch("qb_peer_vpn.map_visualizer.subprocess.run")
def test_render_to_png_chrome_failure_firefox_fallback(
    mock_run, visualizer, sample_clusters, sample_recommendations, tmp_path
):
    """Test PNG rendering falls back to Firefox when Chrome fails."""
    output_file = tmp_path / "test_map.html"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock Chrome failure, Firefox success
    def run_side_effect(cmd, *args, **kwargs):
        if "google-chrome" in cmd:
            raise FileNotFoundError("Chrome not found")
        else:
            return Mock(returncode=0, stderr="")

    mock_run.side_effect = run_side_effect

    # Call render_to_png
    visualizer._render_to_png(str(output_file))

    # Verify both Chrome and Firefox were attempted
    assert mock_run.call_count == 2


@patch("qb_peer_vpn.map_visualizer.subprocess.run")
def test_render_to_png_handles_timeout(
    mock_run, visualizer, sample_clusters, sample_recommendations, tmp_path, capsys
):
    """Test PNG rendering handles timeout gracefully."""
    output_file = tmp_path / "test_map.html"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock timeout
    import subprocess

    mock_run.side_effect = subprocess.TimeoutExpired("chrome", 30)

    # Call render_to_png - should not raise exception
    visualizer._render_to_png(str(output_file))

    # Check warning message was printed
    captured = capsys.readouterr()
    assert "timeout" in captured.out.lower()


def test_create_map_with_render_png_flag(
    visualizer, sample_clusters, sample_recommendations, tmp_path
):
    """Test create_map with render_png=True calls _render_to_png."""
    output_file = tmp_path / "test_map.html"

    with patch.object(visualizer, "_render_to_png") as mock_render:
        visualizer.create_map(
            sample_clusters,
            sample_recommendations,
            output_file=str(output_file),
            render_png=True,
        )

        mock_render.assert_called_once_with(str(output_file))


def test_png_path_matches_html_path(visualizer, tmp_path):
    """Test PNG file has same base name as HTML file."""
    html_file = tmp_path / "my_custom_map.html"
    png_file = tmp_path / "my_custom_map.png"

    # Create a dummy HTML file
    html_file.write_text("<html></html>")

    with patch("qb_peer_vpn.map_visualizer.subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0, stderr="")
        visualizer._render_to_png(str(html_file))

        # Verify the PNG path matches HTML base name
        call_args = mock_run.call_args[0][0]
        assert str(png_file) in " ".join(call_args)
