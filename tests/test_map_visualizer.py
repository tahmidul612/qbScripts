"""Tests for map_visualizer module."""

import pytest
from unittest.mock import patch, MagicMock
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


def test_render_to_png_with_playwright_success(
    visualizer, sample_clusters, sample_recommendations, tmp_path
):
    """Test PNG rendering succeeds with Playwright."""
    output_file = tmp_path / "test_map.html"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock Playwright components
    with patch("qb_peer_vpn.map_visualizer.sync_playwright") as mock_playwright:
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_p.firefox.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Call render_to_png
        visualizer._render_to_png(str(output_file))
        
        # Verify Playwright was used correctly
        mock_p.firefox.launch.assert_called_once_with(headless=True)
        mock_browser.new_page.assert_called_once()
        mock_page.goto.assert_called_once()
        mock_page.screenshot.assert_called_once()
        mock_browser.close.assert_called_once()


def test_render_to_png_handles_import_error(
    visualizer, sample_clusters, sample_recommendations, tmp_path, capsys
):
    """Test PNG rendering handles Playwright not installed."""
    output_file = tmp_path / "test_map.html"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock ImportError for Playwright
    with patch("qb_peer_vpn.map_visualizer.sync_playwright", side_effect=ImportError):
        # Call render_to_png - should not raise exception
        visualizer._render_to_png(str(output_file))

    # Check warning message was printed
    captured = capsys.readouterr()
    assert "playwright not installed" in captured.out.lower()


def test_render_to_png_handles_exception(
    visualizer, sample_clusters, sample_recommendations, tmp_path, capsys
):
    """Test PNG rendering handles generic exceptions gracefully."""
    output_file = tmp_path / "test_map.html"

    # Create the HTML file first
    visualizer.create_map(
        sample_clusters,
        sample_recommendations,
        output_file=str(output_file),
        render_png=False,
    )

    # Mock generic exception
    with patch("qb_peer_vpn.map_visualizer.sync_playwright") as mock_playwright:
        mock_playwright.side_effect = Exception("Test error")
        
        # Call render_to_png - should not raise exception
        visualizer._render_to_png(str(output_file))

    # Check warning message was printed
    captured = capsys.readouterr()
    assert "failed" in captured.out.lower()


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

    with patch("qb_peer_vpn.map_visualizer.sync_playwright") as mock_playwright:
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_p.firefox.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        visualizer._render_to_png(str(html_file))

        # Verify the PNG path was used in screenshot call
        mock_page.screenshot.assert_called_once()
        call_kwargs = mock_page.screenshot.call_args[1]
        assert call_kwargs["path"] == str(png_file)

