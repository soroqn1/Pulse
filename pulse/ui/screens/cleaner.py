from textual.app import ComposeResult

from pulse.ui.components.panels import create_panel
from pulse.ui.screens.base import BaseDashboardScreen


class CleanerScreen(BaseDashboardScreen):
    def compose_panels(self) -> ComposeResult:
        yield create_panel("Soon...", "Cleaner")
