# Usage Guide

## Quick Start

### 1. Installation

```bash
git clone https://github.com/tahmidul612/qbScripts.git
cd qbScripts
uv sync
```

### 2. Enable qBittorrent Web UI

1. Open qBittorrent
1. Go to Tools → Options → Web UI
1. Enable "Web User Interface (Remote control)"
1. Set username and password
1. Note the port (default: 8080)

### 3. Run Analysis

```bash
qb-peer-vpn analyze --username admin
```

Enter your qBittorrent password when prompted.

## Detailed Usage

### Command Line Options

```bash
qb-peer-vpn analyze [OPTIONS]
```

**Required:**

- `--password`: qBittorrent password (will prompt if not provided)

**Optional:**

- `--host TEXT`: qBittorrent host (default: localhost)
- `--port INTEGER`: qBittorrent port (default: 8080)
- `--username TEXT`: qBittorrent username (default: admin)
- `--clusters INTEGER`: Number of peer clusters (default: 5)
- `--map PATH`: Generate HTML map
- `--theme [light|dark]`: Map theme (default: light)

### Examples

#### Basic Analysis

```bash
qb-peer-vpn analyze --username admin
```

This will:

1. Connect to qBittorrent on localhost:8080
1. Fetch all peer IPs from active torrents
1. Geolocate each unique IP
1. Cluster peers by geographic location
1. Recommend ProtonVPN P2P servers for each cluster
1. Display results in a formatted table

#### With Custom Settings

```bash
qb-peer-vpn analyze \
  --host 192.168.1.100 \
  --port 9090 \
  --username myuser \
  --clusters 10
```

#### Generate Interactive Map

```bash
qb-peer-vpn analyze \
  --username admin \
  --map output.html \
  --theme dark
```

Opens a browser with an interactive map showing:

- Your location (green home icon)
- Peer clusters (blue circles, size = peer count)
- Recommended VPN servers (red server icons)
- Lines connecting clusters to recommended servers

### Understanding the Output

#### Terminal Output

```
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Cluster  ┃ Peers ┃ Region         ┃ VPN Server     ┃ Location       ┃ Distance(km) ┃ Load % ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Cluster1 │   125 │ London, UK     │ UK-LON#23      │ London, UK     │ 5.2          │ 45     │
│ Cluster2 │    87 │ New York, US   │ US-NY#103      │ New York, US   │ 12.8         │ 62     │
│ Cluster3 │    64 │ Paris, France  │ FR-PAR#15      │ Paris, France  │ 3.1          │ 38     │
└──────────┴───────┴────────────────┴────────────────┴────────────────┴──────────────┴────────┘
```

**Columns:**

- **Cluster**: Cluster identifier
- **Peers**: Number of peers in this cluster
- **Region**: Geographic location of cluster centroid
- **VPN Server**: Recommended ProtonVPN server
- **Location**: Server location
- **Distance**: Distance from cluster to server (km)
- **Load**: Current server load percentage

#### Map Features

The interactive map includes:

- **Zoom/Pan**: Navigate the map
- **Markers**: Click for detailed information
- **Legend**: Explains map elements
- **Themes**: Light (CartoDB Positron) or Dark (CartoDB Dark Matter)

### Advanced Usage

#### Using as a Library

```python
from qb_peer_vpn.peer_fetcher import QBitPeerFetcher
from qb_peer_vpn.geolocator import IPGeolocator
from qb_peer_vpn.cluster_analyzer import PeerClusterAnalyzer

# Fetch peers
fetcher = QBitPeerFetcher("localhost", 8080, "admin", "pass")
fetcher.connect()
peer_ips = fetcher.get_all_peers()
fetcher.disconnect()

# Geolocate
geolocator = IPGeolocator()
peer_locations = {}
for ip, count in peer_ips.items():
    loc = geolocator.geolocate(ip)
    if loc:
        loc["count"] = count
        peer_locations[ip] = loc

# Cluster and analyze
analyzer = PeerClusterAnalyzer(n_clusters=5)
clusters = analyzer.cluster_peers(peer_locations)
```

See `docs/example.py` for a complete example.

#### Custom Clustering

Adjust the number of clusters based on your torrent activity:

- **Few peers (< 50)**: Use 3-5 clusters
- **Moderate peers (50-200)**: Use 5-8 clusters
- **Many peers (> 200)**: Use 8-15 clusters

```bash
qb-peer-vpn analyze --clusters 12
```

#### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your credentials
```

Then you can run without arguments:

```bash
qb-peer-vpn analyze
```

## Troubleshooting

### Connection Errors

**Problem**: "Failed to connect to qBittorrent"

**Solutions:**

1. Verify qBittorrent is running
1. Check Web UI is enabled in qBittorrent settings
1. Verify host and port are correct
1. Check username and password
1. Try accessing http://localhost:8080 in a browser

### No Peers Found

**Problem**: "No peers found in active torrents"

**Solutions:**

1. Ensure you have active torrents downloading/seeding
1. Wait for torrents to connect to peers
1. Check qBittorrent connection settings

### Geolocation Failures

**Problem**: Many IPs fail to geolocate

**Solutions:**

1. Check internet connection
1. Rate limiting - tool automatically throttles requests
1. Some IPs may not have geolocation data (normal)

### Map Not Generating

**Problem**: Map HTML file is empty or corrupted

**Solutions:**

1. Ensure you have write permissions in the output directory
1. Check disk space
1. Verify Folium is installed: `uv run python -c "import folium"`

## Performance Tips

1. **Caching**: IP geolocations are cached for 1 hour by default
1. **Rate Limiting**: API calls are automatically throttled to 45 req/min
1. **Large Peer Lists**: Analysis time scales with unique IPs (not total peers)
1. **Network**: First run takes longer due to API calls

## API Rate Limits

- **IP-API.com**: 45 requests/minute (free tier)
- **ProtonVPN Server List**: Fetched once per run
- Tool automatically handles rate limiting

## Security Notes

1. **Passwords**: Never commit passwords to version control
1. **Web UI**: Secure your qBittorrent Web UI with strong credentials
1. **Network**: Tool makes HTTPS requests to external APIs
1. **Privacy**: Only IP addresses (no personal data) are sent to geolocation APIs

## FAQ

**Q: How accurate is the geolocation?**
A: City-level accuracy. IP geolocation is approximate and may not reflect actual peer locations.

**Q: Can I use other VPN providers?**
A: The tool currently supports ProtonVPN. PRs welcome for other providers!

**Q: Does this work on Docker?**
A: Yes, if qBittorrent is accessible from the container network.

**Q: Can I schedule automatic analysis?**
A: Yes, use cron or similar scheduling tools to run the CLI command.

**Q: How many torrents can it handle?**
A: Tested with 100+ active torrents. Performance depends on unique peer count.
