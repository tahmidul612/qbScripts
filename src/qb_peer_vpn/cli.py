"""Command-line interface using Typer."""

import typer
from typing import Optional
from pathlib import Path

from .peer_fetcher import QBitPeerFetcher
from .geolocator import IPGeolocator
from .vpn_data import ProtonVPNData
from .cluster_analyzer import PeerClusterAnalyzer
from .ui import TerminalUI
from .map_visualizer import MapVisualizer

app = typer.Typer(help="qBittorrent Peer-IP Clustering & ProtonVPN Server Recommender")


@app.command()
def analyze(
    host: str = typer.Option("localhost", help="qBittorrent host"),
    port: int = typer.Option(8080, help="qBittorrent port"),
    username: str = typer.Option("admin", help="qBittorrent username"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="qBittorrent password"
    ),
    clusters: int = typer.Option(5, help="Number of peer clusters"),
    map_output: Optional[Path] = typer.Option(None, "--map", help="Generate HTML map"),
    theme: str = typer.Option("light", help="Map theme (light/dark)"),
    render_png: bool = typer.Option(False, "--render-png", help="Render map as PNG"),
):
    """Analyze qBittorrent peers and recommend VPN servers."""
    ui = TerminalUI()

    try:
        # Initialize components
        ui.display_info("Connecting to qBittorrent...")
        fetcher = QBitPeerFetcher(host, port, username, password)
        fetcher.connect()

        ui.display_info("Fetching peer data...")
        peer_ips = fetcher.get_all_peers()
        fetcher.disconnect()

        if not peer_ips:
            ui.display_warning("No peers found in active torrents.")
            return

        ui.display_info(f"Found {len(peer_ips)} unique peer IPs")

        # Geolocate peers
        ui.display_info("Geolocating peer IPs (this may take a while)...")
        geolocator = IPGeolocator()
        peer_locations = {}
        total_peers = 0

        for ip, count in peer_ips.items():
            location = geolocator.geolocate(ip)
            if location:
                location["count"] = count
                peer_locations[ip] = location
                total_peers += count

        ui.display_info(f"Successfully geolocated {len(peer_locations)} IPs")

        # Get user location
        user_location = geolocator.get_current_location()

        # Fetch VPN servers
        ui.display_info("Fetching ProtonVPN server data...")
        vpn_data = ProtonVPNData()
        vpn_servers = vpn_data.get_p2p_servers()
        ui.display_info(f"Found {len(vpn_servers)} P2P-enabled VPN servers")

        # Cluster analysis
        ui.display_info("Analyzing peer clusters...")
        analyzer = PeerClusterAnalyzer(n_clusters=clusters)
        peer_clusters = analyzer.cluster_peers(peer_locations)

        # Get recommendations
        recommendations = analyzer.recommend_servers(
            peer_clusters, vpn_servers, user_location
        )

        # Display results
        ui.display_summary(total_peers, len(peer_ips), len(peer_clusters))
        ui.display_recommendations(recommendations, user_location)

        # Generate map if requested
        if map_output:
            ui.display_info("Generating map...")
            visualizer = MapVisualizer(theme=theme)
            visualizer.create_map(
                peer_clusters,
                recommendations,
                user_location,
                str(map_output),
                render_png=render_png,
            )

    except Exception as e:
        ui.display_error(str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
