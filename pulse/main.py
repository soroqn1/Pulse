from textual.app import App

from pulse.ui.screens.cleaner import CleanerScreen
from pulse.ui.screens.docker import DockerScreen
from pulse.ui.screens.menu import MenuScreen
from pulse.ui.screens.monitor import MonitorScreen


class PulseApp(App):
    CSS_PATH = "styles.tcss"

    SCREENS = {
        "menu": MenuScreen,
        "monitor": MonitorScreen,
        "docker": DockerScreen,
        "cleaner": CleanerScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("menu")


def run_app():
    app = PulseApp()
    app.run()

if __name__ == "__main__":
    run_app()
