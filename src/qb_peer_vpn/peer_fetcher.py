"""Module for fetching peer data from qBittorrent."""

from typing import Dict
import qbittorrentapi


class QBitPeerFetcher:
    """Fetch peer data from qBittorrent Web UI."""

    def __init__(self, host: str, port: int, username: str, password: str):
        """Initialize connection to qBittorrent.

        Args:
            host: qBittorrent host address
            port: qBittorrent port number
            username: qBittorrent Web UI username
            password: qBittorrent Web UI password
        """
        self.client = qbittorrentapi.Client(
            host=host, port=port, username=username, password=password
        )

    def connect(self) -> None:
        """Establish connection to qBittorrent."""
        try:
            self.client.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            raise ConnectionError(f"Failed to log in to qBittorrent: {e}")

    def get_all_peers(self) -> Dict[str, int]:
        """Fetch all peer IPs from active torrents.

        Returns:
            Dictionary mapping IP addresses to peer count
        """
        peer_ips = {}
        torrents = self.client.torrents_info()

        for torrent in torrents:
            try:
                peers = self.client.sync_torrent_peers(torrent.hash, rid=0)
                if hasattr(peers, "peers") and peers.peers:
                    for peer_id, peer_data in peers.peers.items():
                        ip = peer_data.get("ip", "")
                        if ip and ip != "":
                            peer_ips[ip] = peer_ips.get(ip, 0) + 1
            except Exception as e:
                print(f"Warning: Failed to fetch peers for torrent {torrent.name}: {e}")
                continue

        return peer_ips

    def disconnect(self) -> None:
        """Close connection to qBittorrent."""
        self.client.auth_log_out()
