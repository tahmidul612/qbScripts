"""Terminal UI module using Rich."""

from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from contextlib import contextmanager


class TerminalUI:
    """Display analysis results in terminal using Rich."""

    def __init__(self):
        """Initialize console."""
        self.console = Console()
        self._progress = None
        self._geo_task = None
        self._spinner_status = None

    def update_geolocation_progress(self, current: int, total: int, ip: str) -> None:
        """Update geolocation progress.

        Args:
            current: Current number of IPs processed
            total: Total number of IPs to process
            ip: Current IP being processed
        """
        if self._progress is None:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
            )
            self._progress.start()
            self._geo_task = self._progress.add_task(
                "[cyan]Geolocating IPs...", total=total
            )

        self._progress.update(self._geo_task, completed=current)

        if current >= total:
            self._progress.stop()
            self._progress = None
            self._geo_task = None

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
                "[bold cyan]🌍 qBittorrent Peer Analysis & VPN Recommendations[/bold cyan]",
                border_style="cyan",
            )
        )

        if user_location:
            self.console.print(
                f"\n[bold yellow]📍 Your Location:[/bold yellow] "
                f"{user_location.get('city', 'Unknown')}, "
                f"{user_location.get('country', 'Unknown')} "
                f"(IP: {user_location.get('ip', 'Unknown')})"
            )

        self.console.print(
            "\n[dim]The table below shows recommended VPN servers for each peer cluster."
        )
        self.console.print(
            "[dim]Connect to servers closer to your peer clusters for better performance.[/dim]\n"
        )

        table = Table(
            title="Recommended VPN Servers by Peer Cluster",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
        )
        table.add_column("Cluster #", style="cyan", width=10, justify="center")
        table.add_column("Peers", justify="right", style="green")
        table.add_column("Peer Region", style="yellow", no_wrap=False)
        table.add_column("VPN Server", style="bold blue", no_wrap=False)
        table.add_column("Server Location", style="white", no_wrap=False)
        table.add_column("Distance (km)", justify="right", style="red")
        table.add_column("Load %", justify="right", style="magenta")

        for i, rec in enumerate(recommendations, 1):
            cluster = rec["cluster"]
            server = rec["server"]

            table.add_row(
                f"{i}",
                str(cluster["peer_count"]),
                f"{cluster['city']}, {cluster['country']}",
                server["name"],
                f"{server['city']}, {server['country']}",
                f"{server.get('distance_to_cluster', 0):.1f}",
                f"{server.get('load', 0):.0f}",
            )

        self.console.print(table)
        self.console.print(
            f"\n[bold green]✓[/bold green] Analysis complete! "
            f"Found {len(recommendations)} optimal server(s) for your peer distribution.\n"
        )

    def display_summary(self, total_peers: int, total_ips: int, clusters: int) -> None:
        """Display summary statistics.

        Args:
            total_peers: Total number of peers
            total_ips: Total unique IP addresses
            clusters: Number of clusters found
        """
        self.console.print("\n[bold green]📊 Summary Statistics:[/bold green]")
        self.console.print(
            f"  [cyan]•[/cyan] Total Peer Connections: [bold]{total_peers}[/bold]"
        )
        self.console.print(
            f"  [cyan]•[/cyan] Unique IP Addresses: [bold]{total_ips}[/bold]"
        )
        self.console.print(
            f"  [cyan]•[/cyan] Geographic Clusters Identified: [bold]{clusters}[/bold]\n"
        )

    def display_error(self, message: str) -> None:
        """Display error message.

        Args:
            message: Error message to display
        """
        self.console.print(f"[bold red]✗ Error:[/bold red] {message}")

    def display_warning(self, message: str) -> None:
        """Display warning message.

        Args:
            message: Warning message to display
        """
        self.console.print(f"[yellow]⚠ Warning:[/yellow] {message}")

    def display_info(self, message: str) -> None:
        """Display info message.

        Args:
            message: Info message to display
        """
        self.console.print(f"[blue]ℹ Info:[/blue] {message}")

    def display_success(self, message: str) -> None:
        """Display success message.

        Args:
            message: Success message to display
        """
        self.console.print(f"[bold green]✓[/bold green] {message}")

    @contextmanager
    def spinner(self, message: str):
        """Context manager for displaying a spinner during long operations.

        Args:
            message: Message to display with the spinner

        Example:
            with ui.spinner("Loading data..."):
                # do work
                pass
        """
        status = self.console.status(f"[cyan]{message}[/cyan]", spinner="dots")
        status.start()
        try:
            yield
        finally:
            status.stop()
