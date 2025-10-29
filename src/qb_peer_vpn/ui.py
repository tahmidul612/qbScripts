"""Terminal UI module using Rich."""

from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class TerminalUI:
    """Display analysis results in terminal using Rich."""

    def __init__(self):
        """Initialize console."""
        self.console = Console()

    def display_recommendations(
        self,
        recommendations: List[Dict],
        user_location: Optional[Dict] = None,
    ) -> None:
        """Display VPN server recommendations.

        Args:
            recommendations: List of recommendation dictionaries
            user_location: Optional user location info
        """
        self.console.print("\n")
        self.console.print(
            Panel(
                "[bold cyan]Optimal VPN Server Recommendations for Better Torrent Performance[/bold cyan]",
                border_style="cyan",
            )
        )

        # Add explanatory text
        self.console.print("\n[dim]💡 Why these recommendations matter:[/dim]")
        self.console.print(
            "[dim]   Connecting to a VPN server near your peers reduces latency and improves download/upload speeds.[/dim]"
        )
        self.console.print(
            "[dim]   Each cluster represents a geographic concentration of peers from your active torrents.[/dim]\n"
        )

        if user_location:
            self.console.print(
                f"[yellow]📍 Your Current Location:[/yellow] {user_location.get('city', 'Unknown')}, "
                f"{user_location.get('country', 'Unknown')}\n"
            )

        # Find the best overall recommendation (largest cluster)
        if recommendations:
            best_rec = max(recommendations, key=lambda r: r["cluster"]["peer_count"])
            self.console.print(
                f"[bold green]⭐ Best Overall Choice:[/bold green] [bold blue]{best_rec['server']['name']}[/bold blue] "
                f"[dim]({best_rec['cluster']['peer_count']} peers in nearby cluster)[/dim]\n"
            )

        table = Table(
            title="VPN Server Recommendations by Peer Cluster",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Priority", style="cyan", width=8, justify="center")
        table.add_column("Peer Cluster Location", style="yellow", no_wrap=True)
        table.add_column("Peers", justify="right", style="green")
        table.add_column("Recommended VPN Server", style="bold blue")
        table.add_column("Server Location", style="white")
        table.add_column("Distance", justify="right", style="red")

        # Sort recommendations by peer count (descending) for priority
        sorted_recs = sorted(
            recommendations, key=lambda r: r["cluster"]["peer_count"], reverse=True
        )

        for i, rec in enumerate(sorted_recs, 1):
            cluster = rec["cluster"]
            server = rec["server"]
            distance = server.get("distance_to_cluster", 0)

            # Add priority indicator
            priority = "★" if i == 1 else str(i)

            # Format distance with units
            if distance < 1:
                distance_str = f"{distance * 1000:.0f} m"
            else:
                distance_str = f"{distance:.0f} km"

            table.add_row(
                priority,
                f"{cluster['city']}, {cluster['country']}",
                str(cluster["peer_count"]),
                server["name"],
                f"{server['city']}, {server['country']}",
                distance_str,
            )

        self.console.print(table)

        # Add helpful footer
        self.console.print(
            "\n[dim]💬 Tip: Connect to the VPN server with the highest priority (★) for optimal performance.[/dim]"
        )

    def display_summary(self, total_peers: int, total_ips: int, clusters: int) -> None:
        """Display summary statistics.

        Args:
            total_peers: Total number of peers
            total_ips: Total unique IP addresses
            clusters: Number of clusters found
        """
        self.console.print("\n[bold green]━━━ Analysis Summary ━━━[/bold green]")
        self.console.print(f"  📊 Total Connections: [bold]{total_peers}[/bold] peers")
        self.console.print(f"  🌐 Unique IP Addresses: [bold]{total_ips}[/bold]")
        self.console.print(
            f"  📍 Geographic Clusters: [bold]{clusters}[/bold] major peer concentration area{'s' if clusters != 1 else ''}\n"
        )

    def display_error(self, message: str) -> None:
        """Display error message.

        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def display_warning(self, message: str) -> None:
        """Display warning message.

        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]Warning:[/yellow] {message}")

    def display_info(self, message: str) -> None:
        """Display info message.

        Args:
            message: Info message to display
        """
        self.console.print(f"[blue]Info:[/blue] {message}")
