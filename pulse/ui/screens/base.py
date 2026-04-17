from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Label


class BaseDashboardScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back to Menu"),
        ("q", "app.exit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield from self.compose_panels()
        yield Label("‹ ESC › Back to Menu", id="back-hint")

    def compose_panels(self) -> ComposeResult:
        return []
