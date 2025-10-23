"""Module for clustering peers and analyzing geographic distribution."""

from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans
from geopy.distance import geodesic


class PeerClusterAnalyzer:
    """Analyze peer distribution and cluster by geography."""

    def __init__(self, n_clusters: int = 5):
        """Initialize analyzer.

        Args:
            n_clusters: Number of clusters to create
        """
        self.n_clusters = n_clusters
        self.clusters = []

    def cluster_peers(self, peer_locations: Dict[str, Dict]) -> List[Dict]:
        """Cluster peers by geographic location.

        Args:
            peer_locations: Dict mapping IP to location data with 'lat', 'lon', 'count'

        Returns:
            List of cluster dictionaries with centroid and peer count
        """
        if not peer_locations:
            return []

        # Prepare data for clustering
        coords = []
        weights = []
        ips = []

        for ip, loc in peer_locations.items():
            if loc and loc.get("lat") is not None and loc.get("lon") is not None:
                coords.append([loc["lat"], loc["lon"]])
                weights.append(loc.get("count", 1))
                ips.append(ip)

        if len(coords) < 2:
            # If only one location, return it as the only cluster
            if coords:
                return [
                    {
                        "centroid": coords[0],
                        "peer_count": weights[0],
                        "ips": [ips[0]],
                        "country": peer_locations[ips[0]].get("country", "Unknown"),
                        "city": peer_locations[ips[0]].get("city", "Unknown"),
                    }
                ]
            return []

        coords_array = np.array(coords)
        weights_array = np.array(weights)

        # Adjust number of clusters if we have fewer locations
        n_clusters = min(self.n_clusters, len(coords))

        # Perform K-means clustering with sample weights
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords_array, sample_weight=weights_array)

        # Calculate weighted centroids and aggregate data
        clusters = []
        for cluster_id in range(n_clusters):
            mask = labels == cluster_id
            cluster_coords = coords_array[mask]
            cluster_weights = weights_array[mask]
            cluster_ips = [ips[i] for i, m in enumerate(mask) if m]

            if len(cluster_coords) == 0:
                continue

            # Calculate weighted centroid
            total_weight = np.sum(cluster_weights)
            weighted_lat = np.average(cluster_coords[:, 0], weights=cluster_weights)
            weighted_lon = np.average(cluster_coords[:, 1], weights=cluster_weights)

            # Get most common country/city in cluster
            countries = [
                peer_locations[ip].get("country", "Unknown") for ip in cluster_ips
            ]
            cities = [peer_locations[ip].get("city", "Unknown") for ip in cluster_ips]
            most_common_country = max(set(countries), key=countries.count)
            most_common_city = max(set(cities), key=cities.count)

            clusters.append(
                {
                    "centroid": [weighted_lat, weighted_lon],
                    "peer_count": int(total_weight),
                    "ips": cluster_ips,
                    "country": most_common_country,
                    "city": most_common_city,
                }
            )

        self.clusters = clusters
        return clusters

    def get_overall_centroid(
        self, peer_locations: Dict[str, Dict]
    ) -> Optional[Tuple[float, float]]:
        """Calculate overall weighted centroid of all peers.

        Args:
            peer_locations: Dict mapping IP to location data

        Returns:
            Tuple of (latitude, longitude) or None
        """
        coords = []
        weights = []

        for ip, loc in peer_locations.items():
            if loc and loc.get("lat") is not None and loc.get("lon") is not None:
                coords.append([loc["lat"], loc["lon"]])
                weights.append(loc.get("count", 1))

        if not coords:
            return None

        coords_array = np.array(coords)
        weights_array = np.array(weights)

        weighted_lat = np.average(coords_array[:, 0], weights=weights_array)
        weighted_lon = np.average(coords_array[:, 1], weights=weights_array)

        return (weighted_lat, weighted_lon)

    def recommend_servers(
        self,
        clusters: List[Dict],
        vpn_servers: List[Dict],
        user_location: Optional[Dict] = None,
    ) -> List[Dict]:
        """Recommend VPN servers for each cluster.

        Args:
            clusters: List of peer clusters
            vpn_servers: List of available VPN servers
            user_location: Optional user location to factor into recommendations

        Returns:
            List of recommendations with cluster and best server
        """
        recommendations = []

        for cluster in clusters:
            centroid = tuple(cluster["centroid"])
            best_server = None
            best_score = float("inf")

            for server in vpn_servers:
                if server.get("lat") is None or server.get("lon") is None:
                    continue

                server_loc = (server["lat"], server["lon"])
                distance = geodesic(centroid, server_loc).kilometers

                # Calculate score (lower is better)
                # Weight by peer count and distance
                score = distance / (cluster["peer_count"] + 1)

                # Factor in user location if provided
                if (
                    user_location
                    and user_location.get("lat")
                    and user_location.get("lon")
                ):
                    user_loc = (user_location["lat"], user_location["lon"])
                    user_distance = geodesic(user_loc, server_loc).kilometers
                    # Prefer servers closer to user
                    score += user_distance * 0.1

                # Prefer servers with lower load
                score += server.get("load", 0) * 0.01

                if score < best_score:
                    best_score = score
                    best_server = server.copy()
                    best_server["distance_to_cluster"] = distance

            if best_server:
                recommendations.append(
                    {
                        "cluster": cluster,
                        "server": best_server,
                        "score": best_score,
                    }
                )

        return recommendations
