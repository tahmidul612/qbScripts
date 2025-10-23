# API Documentation

## Modules

### peer_fetcher

Module for fetching peer data from qBittorrent.

#### QBitPeerFetcher

```python
class QBitPeerFetcher:
    def __init__(self, host: str, port: int, username: str, password: str)
    def connect(self) -> None
    def get_all_peers(self) -> Dict[str, int]
    def disconnect(self) -> None
```

**Example:**

```python
from qb_peer_vpn.peer_fetcher import QBitPeerFetcher

fetcher = QBitPeerFetcher("localhost", 8080, "admin", "password")
fetcher.connect()
peers = fetcher.get_all_peers()  # Returns: {"1.2.3.4": 5, "5.6.7.8": 3}
fetcher.disconnect()
```

### geolocator

Module for IP geolocation with caching.

#### IPGeolocator

```python
class IPGeolocator:
    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 1000)
    def geolocate(self, ip: str) -> Optional[Dict[str, any]]
    def get_current_location(self) -> Optional[Dict[str, any]]
    def geolocate_batch(self, ips: list) -> Dict[str, Optional[Dict]]
```

**Example:**

```python
from qb_peer_vpn.geolocator import IPGeolocator

geolocator = IPGeolocator()
location = geolocator.geolocate("8.8.8.8")
# Returns: {"lat": 37.386, "lon": -122.084, "country": "United States", "city": "Mountain View"}
```

### vpn_data

Module for ProtonVPN server data management.

#### ProtonVPNData

```python
class ProtonVPNData:
    def __init__(self, data_url: Optional[str] = None)
    def fetch_servers(self) -> None
    def get_p2p_servers(self) -> List[Dict]
    def load_from_file(self, filepath: str) -> None
```

**Example:**

```python
from qb_peer_vpn.vpn_data import ProtonVPNData

vpn_data = ProtonVPNData()
p2p_servers = vpn_data.get_p2p_servers()
# Returns list of P2P-enabled servers
```

### cluster_analyzer

Module for clustering peers and analyzing geographic distribution.

#### PeerClusterAnalyzer

```python
class PeerClusterAnalyzer:
    def __init__(self, n_clusters: int = 5)
    def cluster_peers(self, peer_locations: Dict[str, Dict]) -> List[Dict]
    def get_overall_centroid(self, peer_locations: Dict[str, Dict]) -> Optional[Tuple[float, float]]
    def recommend_servers(self, clusters: List[Dict], vpn_servers: List[Dict], user_location: Optional[Dict] = None) -> List[Dict]
```

**Example:**

```python
from qb_peer_vpn.cluster_analyzer import PeerClusterAnalyzer

analyzer = PeerClusterAnalyzer(n_clusters=5)
clusters = analyzer.cluster_peers(peer_locations)
recommendations = analyzer.recommend_servers(clusters, vpn_servers, user_location)
```

### ui

Terminal UI module using Rich.

#### TerminalUI

```python
class TerminalUI:
    def __init__(self)
    def display_recommendations(self, recommendations: List[Dict], user_location: Optional[Dict] = None) -> None
    def display_summary(self, total_peers: int, total_ips: int, clusters: int) -> None
    def display_error(self, message: str) -> None
    def display_warning(self, message: str) -> None
    def display_info(self, message: str) -> None
```

### map_visualizer

Map visualization module using Folium.

#### MapVisualizer

```python
class MapVisualizer:
    def __init__(self, theme: str = "light")
    def create_map(self, clusters: List[Dict], recommendations: List[Dict], user_location: Optional[Dict] = None, output_file: str = "peer_vpn_map.html") -> None
```

**Example:**

```python
from qb_peer_vpn.map_visualizer import MapVisualizer

visualizer = MapVisualizer(theme="dark")
visualizer.create_map(clusters, recommendations, user_location, "output.html")
```

## CLI

### Commands

#### analyze

Analyze qBittorrent peers and recommend VPN servers.

```bash
qb-peer-vpn analyze [OPTIONS]
```

**Options:**

- `--host TEXT`: qBittorrent host (default: localhost)
- `--port INTEGER`: qBittorrent port (default: 8080)
- `--username TEXT`: qBittorrent username (default: admin)
- `--password TEXT`: qBittorrent password (prompted)
- `--clusters INTEGER`: Number of peer clusters (default: 5)
- `--map PATH`: Generate HTML map to specified file
- `--theme TEXT`: Map theme - light or dark (default: light)

**Examples:**

```bash
# Basic usage
qb-peer-vpn analyze --username admin

# With map generation
qb-peer-vpn analyze --username admin --map peers.html --theme dark

# Custom clustering
qb-peer-vpn analyze --username admin --clusters 10
```
