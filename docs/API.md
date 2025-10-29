# API Documentation

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Modules](#modules)
  - [peer_fetcher](#peer_fetcher)
    - [QBitPeerFetcher](#qbitpeerfetcher)
  - [geolocator](#geolocator)
    - [IPGeolocator](#ipgeolocator)
  - [vpn_data](#vpn_data)
    - [ProtonVPNData](#protonvpndata)
  - [cluster_analyzer](#cluster_analyzer)
    - [PeerClusterAnalyzer](#peerclusteranalyzer)
  - [ui](#ui)
    - [TerminalUI](#terminalui)
  - [map_visualizer](#map_visualizer)
    - [MapVisualizer](#mapvisualizer)
- [CLI](#cli)
  - [Command](#command)

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

**Methods:**

- `connect()`: Establishes connection to qBittorrent Web UI
- `get_all_peers()`: Returns dictionary mapping peer IPs to connection counts
- `disconnect()`: Closes connection to qBittorrent

**Example:**

```python
from qb_peer_vpn.peer_fetcher import QBitPeerFetcher

fetcher = QBitPeerFetcher("localhost", 8080, "admin", "password")
fetcher.connect()
peers = fetcher.get_all_peers()  # Returns: {"1.2.3.4": 5, "5.6.7.8": 3}
fetcher.disconnect()
```

### geolocator

Module for IP geolocation with caching and batch processing.

#### IPGeolocator

```python
class IPGeolocator:
    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 1000)
    def geolocate(self, ip: str) -> Optional[Dict[str, any]]
    def get_current_location(self) -> Optional[Dict[str, any]]
    def geolocate_batch(self, ips: List[str], progress_callback: Optional[Callable] = None) -> Dict[str, Optional[Dict]]
```

**Methods:**

- `geolocate(ip)`: Geolocate a single IP address
- `get_current_location()`: Get the user's current location based on their public IP
- `geolocate_batch(ips, progress_callback)`: Batch geolocate multiple IPs (up to 100 per request)
  - Uses IP-API.com batch endpoint for primary lookups
  - Automatically falls back to ipapi.co and freeipapi.com for failed lookups
  - Supports optional progress callback for UI updates

**Features:**

- TTL-based caching to minimize API calls
- Batch processing (up to 100 IPs per request)
- Multiple provider fallback (IP-API.com → ipapi.co → freeipapi.com)
- Rate limiting respect (15 requests/minute for batch endpoint)

**Example:**

```python
from qb_peer_vpn.geolocator import IPGeolocator

geolocator = IPGeolocator()

# Single IP
location = geolocator.geolocate("8.8.8.8")
# Returns: {"lat": 37.386, "lon": -122.084, "country": "United States", "city": "Mountain View"}

# Batch processing
ips = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
results = geolocator.geolocate_batch(ips)
# Returns: {"8.8.8.8": {...}, "1.1.1.1": {...}, "9.9.9.9": {...}}
```

### vpn_data

Module for ProtonVPN server data management.

#### ProtonVPNData

```python
class ProtonVPNData:
    def __init__(self, data_url: Optional[str] = None)
    def fetch_servers(self) -> None
    def get_p2p_servers(self, geocode: bool = True) -> List[Dict]
    def load_from_file(self, filepath: str) -> None
```

**Methods:**

- `fetch_servers()`: Fetches latest ProtonVPN server data from remote source
- `get_p2p_servers(geocode)`: Returns list of P2P-enabled servers, optionally with geocoding
- `load_from_file(filepath)`: Load server data from local file

**Example:**

```python
from qb_peer_vpn.vpn_data import ProtonVPNData

vpn_data = ProtonVPNData()
p2p_servers = vpn_data.get_p2p_servers(geocode=True)
# Returns list of P2P-enabled servers with lat/lon coordinates
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

**Methods:**

- `cluster_peers(peer_locations)`: Cluster peers geographically using K-means
- `get_overall_centroid(peer_locations)`: Calculate overall centroid of all peers
- `recommend_servers(clusters, vpn_servers, user_location)`: Recommend optimal VPN servers for each cluster

**Example:**

```python
from qb_peer_vpn.cluster_analyzer import PeerClusterAnalyzer

analyzer = PeerClusterAnalyzer(n_clusters=5)
clusters = analyzer.cluster_peers(peer_locations)
recommendations = analyzer.recommend_servers(clusters, vpn_servers, user_location)
```

### ui

Terminal UI module using Rich for beautiful console output.

#### TerminalUI

```python
class TerminalUI:
    def __init__(self)
    def display_recommendations(self, recommendations: List[Dict], user_location: Optional[Dict] = None) -> None
    def display_summary(self, total_peers: int, total_ips: int, clusters: int) -> None
    def display_error(self, message: str) -> None
    def display_warning(self, message: str) -> None
    def display_info(self, message: str) -> None
    def display_success(self, message: str) -> None
    def update_geolocation_progress(self, current: int, total: int) -> None
    def spinner(self, message: str) -> ContextManager
```

**Methods:**

- `display_recommendations(recommendations, user_location)`: Show VPN server recommendations in formatted table
- `display_summary(total_peers, total_ips, clusters)`: Display analysis summary
- `display_error(message)`: Show error message
- `display_warning(message)`: Show warning message
- `display_info(message)`: Show info message
- `display_success(message)`: Show success message
- `update_geolocation_progress(current, total)`: Update geolocation progress bar
- `spinner(message)`: Context manager for spinner with message

**Example:**

```python
from qb_peer_vpn.ui import TerminalUI

ui = TerminalUI()
ui.display_info("Processing peers...")
with ui.spinner("Fetching data..."):
    # Long-running operation
    pass
ui.display_success("Complete!")
```

### map_visualizer

Map visualization module using Folium for interactive maps.

#### MapVisualizer

```python
class MapVisualizer:
    def __init__(self, theme: str = "light")
    def create_map(
        self,
        clusters: List[Dict],
        recommendations: List[Dict],
        user_location: Optional[Dict] = None,
        output_file: str = "peer_vpn_map.html",
        render_png: bool = False
    ) -> None
```

**Methods:**

- `create_map(...)`: Generate interactive HTML map with peer clusters and VPN servers
  - **clusters**: List of peer clusters to visualize
  - **recommendations**: List of server recommendations
  - **user_location**: Optional user location to display
  - **output_file**: Output HTML filename
  - **render_png**: If True, also renders map as PNG using Playwright

**Features:**

- Interactive HTML maps with zoom/pan
- Visual cluster representation sized by peer count
- VPN server markers with server details
- Connection lines between clusters and recommended servers
- Dark/light theme support
- Optional PNG export (requires Playwright + Firefox)

**Example:**

```python
from qb_peer_vpn.map_visualizer import MapVisualizer

# Light theme HTML only
visualizer = MapVisualizer(theme="light")
visualizer.create_map(clusters, recommendations, user_location, "output.html")

# Dark theme with PNG export
visualizer = MapVisualizer(theme="dark")
visualizer.create_map(
    clusters,
    recommendations,
    user_location,
    "output.html",
    render_png=True,  # Creates both output.html and output.png
)
```

## CLI

The command-line interface is built with Typer and provides a single command.

### Command

```bash
qb-peer-vpn [OPTIONS]
```

Analyze qBittorrent peers and recommend VPN servers.

**Options:**

- `--host TEXT`: qBittorrent host address (default: `localhost`)
- `--port INTEGER`: qBittorrent port number (default: `8080`)
- `--username TEXT`: qBittorrent Web UI username (default: `admin`)
- `--password TEXT`: qBittorrent password (required, prompted if not provided)
- `--clusters INTEGER`: Number of peer clusters to create (default: `5`)
- `--map PATH`: Generate HTML map to specified file
- `--theme TEXT`: Map theme - `light` or `dark` (default: `light`)
- `--render-png`: Also render the HTML map as a PNG image (requires Playwright)

**Examples:**

```bash
# Basic usage (prompts for password)
qb-peer-vpn --username admin

# Provide password directly
qb-peer-vpn --username admin --password mypassword

# Generate HTML map with dark theme
qb-peer-vpn --username admin --password mypassword --map peers.html --theme dark

# Generate both HTML and PNG
qb-peer-vpn --username admin --password mypassword --map peers.html --render-png

# Custom host, port, and clustering
qb-peer-vpn --host 192.168.1.100 --port 8091 --username admin --password mypassword --clusters 10

# Full example with all options
qb-peer-vpn \
  --host localhost \
  --port 8080 \
  --username admin \
  --password mypassword \
  --clusters 7 \
  --map output.html \
  --render-png \
  --theme dark
```
