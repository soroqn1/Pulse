from textual.app import ComposeResult
from textual.containers import Center, Container, Middle
from textual.screen import Screen
from textual.widgets import OptionList, Static

from pulse.ui.components.logo import AnimatedLogo

COLOR_DANGER = "#E53935"

MENU_OPTIONS = [
    "1. Activity Monitor",
    "2. Docker (Lazy mode)",
    "3. Cleaner",
    "q. Exit",
]


class MenuScreen(Screen):
    BINDINGS = [
        ("1", "select_system", "System"),
        ("2", "select_docker", "Docker"),
        ("3", "select_cleaner", "Cleaner"),
        ("q", "exit_app", "Exit"),
        ("y", "confirm_exit", "Yes"),
        ("n", "cancel_exit", "No"),
    ]

    def compose(self) -> ComposeResult:
        self.confirming_exit = False
        screen_panel = Container(id="full-screen-panel", classes="panel")
        try:
            from importlib.metadata import version

            app_version = f"v{version('pulse')}"
        except Exception:
            app_version = "v0.0.0"

        screen_panel.border_subtitle = app_version
        with screen_panel:
            with Middle():
                with Center():
                    yield AnimatedLogo(id="logo")
                    yield Static("system pulse. always alive.", id="subtitle")
                with Center():
                    with Container(id="menu-wrapper"):
                        yield OptionList(*MENU_OPTIONS, id="main-menu")

    def _is_idle(self) -> bool:
        return not self.confirming_exit

    def action_select_system(self) -> None:
        if not self._is_idle():
            return
        self.app.push_screen("monitor")

    def action_select_docker(self) -> None:
        if not self._is_idle():
            return
        self.app.push_screen("docker")

    def action_select_cleaner(self) -> None:
        if not self._is_idle():
            return
        self.app.push_screen("cleaner")

    def action_exit_app(self) -> None:
        if not self._is_idle():
            return
        self.confirming_exit = True
        menu = self.query_one("#main-menu", OptionList)
        menu.border_title = f"[b][{COLOR_DANGER}]Terminate?[/{COLOR_DANGER}][/b]"
        menu.clear_options()
        menu.add_options(["y. Yes, terminate", "n. No, go back"])

    def action_confirm_exit(self) -> None:
        if self.confirming_exit:
            self.app.exit()

    def action_cancel_exit(self) -> None:
        if self.confirming_exit:
            self.confirming_exit = False
            menu = self.query_one("#main-menu", OptionList)
            menu.border_title = ""
            menu.clear_options()
            menu.add_options(MENU_OPTIONS)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if self.confirming_exit:
            if event.option_index == 0:
                self.action_confirm_exit()
            elif event.option_index == 1:
                self.action_cancel_exit()
        else:
            if event.option_index == 0:
                self.action_select_system()
            elif event.option_index == 1:
                self.action_select_docker()
            elif event.option_index == 2:
                self.action_select_cleaner()
            elif event.option_index == 3:
                self.action_exit_app()
