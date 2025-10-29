"""Map visualization module using Folium."""

from typing import List, Dict, Optional
from pathlib import Path
import folium


class MapVisualizer:
    """Create interactive maps with peer and VPN server data."""

    def __init__(self, theme: str = "light"):
        """Initialize map visualizer.

        Args:
            theme: Map theme ('light' or 'dark')
        """
        self.theme = theme
        self.tile_layer = (
            "CartoDB positron" if theme == "light" else "CartoDB dark_matter"
        )

    def create_map(
        self,
        clusters: List[Dict],
        recommendations: List[Dict],
        user_location: Optional[Dict] = None,
        output_file: str = "peer_vpn_map.html",
        render_png: bool = False,
    ) -> None:
        """Create and save interactive map.

        Args:
            clusters: List of peer clusters
            recommendations: List of server recommendations
            user_location: Optional user location
            output_file: Output HTML filename
            render_png: Whether to also render the map as PNG
        """
        # Calculate map center
        if clusters:
            center_lat = sum(c["centroid"][0] for c in clusters) / len(clusters)
            center_lon = sum(c["centroid"][1] for c in clusters) / len(clusters)
        elif user_location:
            center_lat = user_location.get("lat", 0)
            center_lon = user_location.get("lon", 0)
        else:
            center_lat, center_lon = 0, 0

        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=4,
            tiles=self.tile_layer,
        )

        # Add user location
        if user_location and user_location.get("lat") and user_location.get("lon"):
            folium.Marker(
                location=[user_location["lat"], user_location["lon"]],
                popup=f"Your Location: {user_location.get('city', 'Unknown')}",
                icon=folium.Icon(color="green", icon="home", prefix="fa"),
            ).add_to(m)

        # Add peer clusters
        for i, cluster in enumerate(clusters, 1):
            lat, lon = cluster["centroid"]
            popup_text = (
                f"<b>Cluster {i}</b><br>"
                f"Peers: {cluster['peer_count']}<br>"
                f"Location: {cluster['city']}, {cluster['country']}"
            )

            folium.CircleMarker(
                location=[lat, lon],
                radius=cluster["peer_count"] / 2 + 5,
                popup=folium.Popup(popup_text, max_width=300),
                color="blue",
                fill=True,
                fillColor="blue",
                fillOpacity=0.4,
            ).add_to(m)

        # Add recommended VPN servers and draw lines to clusters
        for i, rec in enumerate(recommendations, 1):
            server = rec["server"]
            cluster = rec["cluster"]

            if server.get("lat") and server.get("lon"):
                # Add server marker
                popup_text = (
                    f"<b>{server['name']}</b><br>"
                    f"Location: {server['city']}, {server['country']}<br>"
                    f"Load: {server.get('load', 0):.0f}%<br>"
                    f"Distance to cluster: {server.get('distance_to_cluster', 0):.1f} km"
                )

                folium.Marker(
                    location=[server["lat"], server["lon"]],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color="red", icon="server", prefix="fa"),
                ).add_to(m)

                # Draw line from cluster to server
                folium.PolyLine(
                    locations=[
                        cluster["centroid"],
                        [server["lat"], server["lon"]],
                    ],
                    color="purple",
                    weight=2,
                    opacity=0.6,
                    dash_array="5, 5",
                ).add_to(m)

        # Add legend
        legend_html = """
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 200px; height: auto;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <p><b>Legend</b></p>
        <p><i class="fa fa-home" style="color:green"></i> Your Location</p>
        <p><i class="fa fa-circle" style="color:blue"></i> Peer Clusters</p>
        <p><i class="fa fa-server" style="color:red"></i> VPN Servers</p>
        <p style="border-top: 2px dashed purple; margin: 5px 0;"></p>
        <p style="font-size:12px;">Dashed lines connect clusters to recommended servers</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        # Save map
        m.save(output_file)
        print(f"Map saved to {output_file}")

        # Render PNG if requested
        if render_png:
            self._render_to_png(output_file)

    def _render_to_png(self, html_file: str) -> None:
        """Render HTML map to PNG using Playwright.

        Args:
            html_file: Path to HTML file to render
        """
        html_path = Path(html_file).resolve()
        png_path = html_path.with_suffix(".png")

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                # Use Firefox in headless mode as requested
                browser = p.firefox.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                
                # Load the HTML file
                page.goto(f"file://{html_path}")
                
                # Wait for the map to render
                page.wait_for_timeout(2000)
                
                # Take screenshot
                page.screenshot(path=str(png_path), full_page=False)
                
                browser.close()
                
            print(f"PNG rendered to {png_path}")

        except ImportError:
            print(
                "Warning: Playwright not installed. Install with: "
                "pip install playwright && playwright install firefox"
            )
        except Exception as e:
            print(f"Warning: PNG rendering failed: {e}")

