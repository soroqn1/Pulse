from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Log, Static, Label
from textual.coordinate import Coordinate

from pulse.services.docker_client import (
    get_containers,
    get_container_logs,
    start_container,
    stop_container,
    restart_container,
)
from pulse.ui.components.panels import create_panel
from pulse.ui.screens.base import BaseDashboardScreen


class ContainerTable(DataTable):
    def on_mount(self) -> None:
        self.col_keys = self.add_columns("Short ID", "Name", "Status", "Image")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_containers()

    def refresh_containers(self) -> None:
        containers = get_containers()
        current_rows = {row_key.value: row_key for row_key in self.rows}
        new_ids = {c.id[:10] for c in containers}

        # Remove old rows
        for c_id, row_key in current_rows.items():
            if c_id not in new_ids:
                self.remove_row(row_key)

        # Add or update rows
        for c in containers:
            c_id = c.id[:10]
            if c_id not in current_rows:
                self.add_row(
                    c_id,
                    c.name,
                    c.status,
                    c.image.tags[0] if c.image.tags else c.attrs['Config']['Image'],
                    key=c_id,
                )
            else:
                self.update_cell(c_id, self.col_keys[1], c.name)
                self.update_cell(c_id, self.col_keys[2], c.status)


class ContainerLog(Log):
    pass


class DockerPanel(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="docker-list-container"):
                yield ContainerTable(id="container-table")
                yield Label(
                    "Hotkeys: [b]s[/b]tart, [b]x[/b] stop, [b]r[/b]estart, [b]f[/b]resh",
                    id="docker-hints",
                )
            with Vertical(id="docker-logs-container"):
                yield ContainerLog(id="container-log", highlight=True)

    def on_mount(self) -> None:
        self.set_interval(2.0, self.update_table)

    def update_table(self) -> None:
        table = self.query_one(ContainerTable)
        table.refresh_containers()

    def fetch_logs(self, container_id: str) -> None:
        log_widget = self.query_one(ContainerLog)
        logs = get_container_logs(container_id, tail=50)
        log_widget.clear()
        
        if not logs:
            log_widget.write("[No logs available]")
        else:
            log_widget.write(logs)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Load logs when a container is selected
        container_id = event.row_key.value
        self.fetch_logs(container_id)


class DockerScreen(BaseDashboardScreen):
    BINDINGS = [
        ("s", "start_container", "Start"),
        ("x", "stop_container", "Stop"),
        ("r", "restart_container", "Restart"),
        ("f", "refresh_containers", "Refresh"),
    ] + BaseDashboardScreen.BINDINGS

    def compose_panels(self) -> ComposeResult:
        yield create_panel(DockerPanel(), "Docker (LazyMode)")

    def get_selected_container_id(self) -> str | None:
        table = self.query_one(ContainerTable)
        if not table.rows:
            return None
        cursor_row = table.cursor_row
        row_key, _ = list(table.rows.items())[cursor_row]
        return row_key.value

    def action_start_container(self) -> None:
        container_id = self.get_selected_container_id()
        if container_id:
            start_container(container_id)
            self.query_one(DockerPanel).update_table()

    def action_stop_container(self) -> None:
        container_id = self.get_selected_container_id()
        if container_id:
            stop_container(container_id)
            self.query_one(DockerPanel).update_table()

    def action_restart_container(self) -> None:
        container_id = self.get_selected_container_id()
        if container_id:
            restart_container(container_id)
            self.query_one(DockerPanel).update_table()

    def action_refresh_containers(self) -> None:
        self.query_one(DockerPanel).update_table()
