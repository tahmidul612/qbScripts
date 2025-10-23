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
                "[bold cyan]qBittorrent Peer Analysis & VPN Recommendations[/bold cyan]",
                border_style="cyan",
            )
        )

        if user_location:
            self.console.print(
                f"\n[yellow]Your Location:[/yellow] {user_location.get('city', 'Unknown')}, "
                f"{user_location.get('country', 'Unknown')}"
            )

        table = Table(
            title="\nRecommended VPN Servers",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Cluster", style="cyan", width=12)
        table.add_column("Peers", justify="right", style="green")
        table.add_column("Region", style="yellow")
        table.add_column("VPN Server", style="bold blue")
        table.add_column("Location", style="white")
        table.add_column("Distance (km)", justify="right", style="red")
        table.add_column("Load %", justify="right", style="magenta")

        for i, rec in enumerate(recommendations, 1):
            cluster = rec["cluster"]
            server = rec["server"]

            table.add_row(
                f"Cluster {i}",
                str(cluster["peer_count"]),
                f"{cluster['city']}, {cluster['country']}",
                server["name"],
                f"{server['city']}, {server['country']}",
                f"{server.get('distance_to_cluster', 0):.1f}",
                f"{server.get('load', 0):.0f}",
            )

        self.console.print(table)

    def display_summary(self, total_peers: int, total_ips: int, clusters: int) -> None:
        """Display summary statistics.

        Args:
            total_peers: Total number of peers
            total_ips: Total unique IP addresses
            clusters: Number of clusters found
        """
        self.console.print("\n[bold green]Summary:[/bold green]")
        self.console.print(f"  • Total Peers: {total_peers}")
        self.console.print(f"  • Unique IPs: {total_ips}")
        self.console.print(f"  • Clusters: {clusters}\n")

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
