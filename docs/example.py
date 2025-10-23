"""Example usage of the qb_peer_vpn library."""

from qb_peer_vpn.peer_fetcher import QBitPeerFetcher
from qb_peer_vpn.geolocator import IPGeolocator
from qb_peer_vpn.vpn_data import ProtonVPNData
from qb_peer_vpn.cluster_analyzer import PeerClusterAnalyzer
from qb_peer_vpn.ui import TerminalUI
from qb_peer_vpn.map_visualizer import MapVisualizer


def main():
    """Example workflow."""
    ui = TerminalUI()

    # 1. Fetch peers from qBittorrent
    ui.display_info("Connecting to qBittorrent...")
    fetcher = QBitPeerFetcher("localhost", 8080, "admin", "your_password")
    try:
        fetcher.connect()
        peer_ips = fetcher.get_all_peers()
        fetcher.disconnect()
        ui.display_info(f"Found {len(peer_ips)} unique peer IPs")
    except ConnectionError as e:
        ui.display_error(f"Failed to connect to qBittorrent: {e}")
        return

    # 2. Geolocate peer IPs
    ui.display_info("Geolocating peer IPs...")
    geolocator = IPGeolocator()
    peer_locations = {}

    for ip, count in peer_ips.items():
        location = geolocator.geolocate(ip)
        if location:
            location["count"] = count
            peer_locations[ip] = location

    # 3. Get user location
    user_location = geolocator.get_current_location()

    # 4. Fetch VPN servers
    ui.display_info("Fetching ProtonVPN server data...")
    vpn_data = ProtonVPNData()
    vpn_servers = vpn_data.get_p2p_servers()

    # 5. Cluster analysis
    ui.display_info("Analyzing peer clusters...")
    analyzer = PeerClusterAnalyzer(n_clusters=5)
    clusters = analyzer.cluster_peers(peer_locations)

    # 6. Get recommendations
    recommendations = analyzer.recommend_servers(clusters, vpn_servers, user_location)

    # 7. Display results
    ui.display_recommendations(recommendations, user_location)

    # 8. Generate map (optional)
    visualizer = MapVisualizer(theme="light")
    visualizer.create_map(clusters, recommendations, user_location, "peer_map.html")


if __name__ == "__main__":
    main()
