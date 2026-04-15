import math
import time

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, Middle
from textual.screen import Screen
from textual.widgets import DataTable, Label, OptionList, Static

from pulse.metrics import get_active_processes, get_all_metrics

COLOR_DANGER = "#E53935"

MENU_OPTIONS = [
    "1. System",
    "2. Docker (Lazy mode)",
    "3. Cleaner",
    "q. Exit",
]


class AnimatedLogo(Static):
    LOGO_LINES = [
        r"    ____  __  ____   _____ ______",
        r"   / __ \/ / / / /  / ___// ____/",
        r"  / /_/ / / / / /   \__ \/ __/   ",
        r" / ____/ /_/ / /______/ / /___   ",
        r"/_/    \____/_____/____/_____/   ",
    ]

    def on_mount(self) -> None:
        self.start_time = time.time()
        self.set_interval(0.05, self.animate_logo)

    def animate_logo(self) -> None:
        current_time = time.time() - self.start_time

        styled_text = Text()
        for i, line in enumerate(self.LOGO_LINES):
            for j, char in enumerate(line):
                if char.isspace():
                    styled_text.append(char)
                    continue

                phase = current_time * 2.0 - j * 0.15 + i * 0.2
                intensity = (math.sin(phase) + 1.0) / 2.0

                r = int(180 + 75 * intensity)
                g = int(10 + 200 * intensity)
                b = int(10 + 100 * intensity)

                color = f"#{r:02x}{g:02x}{b:02x}"
                styled_text.append(char, style=color)
            styled_text.append("\n")

        self.update(styled_text)


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
        screen_panel.border_subtitle = "v0.1.0"
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


class SystemMetrics(Static):
    def on_mount(self) -> None:
        self.update_metrics()
        self.set_interval(1, self.update_metrics)

    def update_metrics(self) -> None:
        data = get_all_metrics()
        cpu = data["cpu_usage"]
        mem = data["memory_usage"]
        mem_used = mem["used"] / (1024**3)
        mem_avail = mem["available"] / (1024**3)
        mem_total = mem["total"] / (1024**3)

        vidget_stat = (
            f"[b][{COLOR_DANGER}]CPU[/{COLOR_DANGER}][/b] Used: {cpu:.1f}% | Free: {100 - cpu:.1f}%\n"
            f"[b][{COLOR_DANGER}]RAM[/{COLOR_DANGER}][/b] Used: {mem_used:.1f} GB | Free: {mem_avail:.1f} GB | Total: {mem_total:.1f} GB"
        )
        self.update(vidget_stat)


class ProcessTable(DataTable):
    def on_mount(self) -> None:
        self.col_keys = self.add_columns("PID", "Name", "User", "CPU (%)", "Mem (MB)")
        self.cursor_type = "row"
        self.zebra_stripes = True

        self.update_processes()
        self.set_interval(2.0, self.update_processes)

    def update_processes(self) -> None:
        processes = get_active_processes(limit=50)

        current_rows = {row_key.value: row_key for row_key in self.rows}
        new_pids = {str(p["pid"]) for p in processes}

        # Remove old rows
        for pid, row_key in current_rows.items():
            if pid not in new_pids:
                self.remove_row(row_key)

        # Add or update rows
        for p in processes:
            pid = str(p["pid"])
            if pid not in current_rows:
                self.add_row(
                    pid,
                    p["name"],
                    p["user"],
                    f"{p['cpu']:.1f}",
                    f"{p['mem_mb']:.1f}",
                    key=pid,
                )
            else:
                self.update_cell(pid, self.col_keys[3], f"{p['cpu']:.1f}")
                self.update_cell(pid, self.col_keys[4], f"{p['mem_mb']:.1f}")


def create_panel(content: str | Static, title: str) -> Static:
    panel = Static(content) if isinstance(content, str) else content
    panel.add_class("panel")
    panel.border_title = title
    panel.border_subtitle = "Pulse"
    panel.border_subtitle_align = "right"
    return panel


class BaseDashboardScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back to Menu"), ("q", "app.exit", "Quit")]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield from self.compose_panels()
        yield Label("‹ ESC › Back to Menu", id="back-hint")

    def compose_panels(self) -> ComposeResult:
        return []


class SystemMonitorPanel(Container):
    def compose(self) -> ComposeResult:
        yield SystemMetrics()
        yield ProcessTable()


class MonitorScreen(BaseDashboardScreen):
    def compose_panels(self) -> ComposeResult:
        yield create_panel(SystemMonitorPanel(), "System & Activity Monitor")


class DockerScreen(BaseDashboardScreen):
    def compose_panels(self) -> ComposeResult:
        yield create_panel("Soon...", "Docker Containers")


class CleanerScreen(BaseDashboardScreen):
    def compose_panels(self) -> ComposeResult:
        yield create_panel("Soon...", "Cleaner")


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


if __name__ == "__main__":
    app = PulseApp()
    app.run()
