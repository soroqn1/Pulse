from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Label, Log

from pulse.services.docker_client import (
    get_container_logs,
    get_containers,
    remove_container,
    restart_container,
    start_container,
    stop_container,
)
from pulse.ui.components.panels import create_panel
from pulse.ui.screens.base import BaseDashboardScreen

STATUS_WEIGHT = {
    "running": 0,
    "restarting": 0,
    "paused": 1,
    "exited": 2,
    "created": 2,
    "dead": 2,
}
STATUS_ICONS = {"running": "running", "paused": "paused", "exited": "exited"}


def get_status_weight(status: str) -> int:
    return STATUS_WEIGHT.get(status, 2)


def get_status_icon(status: str) -> str:
    return STATUS_ICONS.get(status, status)


class ContainerTable(DataTable):
    def on_mount(self) -> None:
        self.col_keys = self.add_columns("Status", "Name", "Project / ID", "Image")
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.refresh_containers()

    def rebuild_table_if_needed(self, containers) -> None:
        fingerprint = hash(tuple((c.id, c.status, c.name) for c in containers))
        if getattr(self, "_last_fingerprint", None) == fingerprint:
            return
        self._last_fingerprint = fingerprint

        groups = {}
        for c in containers:
            project = c.labels.get("com.docker.compose.project", "Standalone")
            groups.setdefault(project, []).append(c)

        group_weights = {}
        for project, items in groups.items():
            items.sort(key=lambda x: (get_status_weight(x.status), x.name))
            group_weights[project] = min(get_status_weight(x.status) for x in items)

        sorted_projects = sorted(groups.keys(), key=lambda p: (group_weights[p], p))

        old_cursor = self.cursor_row
        old_keys = list(self.rows.keys())
        old_selected_key = (
            old_keys[old_cursor].value
            if old_keys and old_cursor < len(old_keys)
            else None
        )

        self.clear(columns=False)

        current_row_idx = 0
        new_cursor_idx = 0

        for project in sorted_projects:
            if current_row_idx > 0:
                self.add_row("", "", "", "", key=f"spacer:{project}")
                current_row_idx += 1

            proj_key = f"project:{project}"
            self.add_row(f"[b]{project}[/b]", "", "", "", key=proj_key)
            if old_selected_key == proj_key:
                new_cursor_idx = current_row_idx
            current_row_idx += 1

            for c in groups[project]:
                c_id = c.id[:10]
                self.add_row(
                    f"  {get_status_icon(c.status)}",
                    f"  {c.name}",
                    f"  {c_id}",
                    c.image.tags[0] if c.image.tags else c.attrs["Config"]["Image"],
                    key=c_id,
                )
                if old_selected_key == c_id:
                    new_cursor_idx = current_row_idx
                current_row_idx += 1

        self.move_cursor(row=new_cursor_idx)

    def refresh_containers(self) -> None:
        containers = get_containers()
        self.rebuild_table_if_needed(containers)


class ContainerLog(Log):
    pass


class DockerPanel(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="docker-list-container"):
                yield ContainerTable(id="container-table")
                yield Label(
                    "Hotkeys: [b]s[/b] start, [b]x[/b] stop, [b]r[/b] restart, [b]d[/b] delete, [b]f[/b] refresh",
                    id="docker-hints",
                )
            with Vertical(id="docker-logs-container"):
                yield ContainerLog(id="container-log", highlight=True)

    def on_mount(self) -> None:
        self.set_interval(2.0, self.update_table)

    def update_table(self) -> None:
        table = self.query_one(ContainerTable)
        table.refresh_containers()

    from textual import work

    @work(exclusive=True, thread=True)
    def fetch_logs(self, container_id: str) -> None:
        def update_log(content):
            log_widget = self.query_one(ContainerLog)
            log_widget.clear()
            log_widget.write(content)

        if container_id.startswith("project:") or container_id.startswith("spacer:"):
            self.app.call_from_thread(update_log, "[Select a container to view logs]")
            return

        logs = get_container_logs(container_id, tail=50)

        if not logs or logs.startswith("Error:"):
            self.app.call_from_thread(
                update_log, f"[No logs available or error: {logs}]"
            )
        else:
            self.app.call_from_thread(update_log, logs)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        container_id = event.row_key.value
        self.fetch_logs(container_id)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        container_id = event.row_key.value
        self.fetch_logs(container_id)


class DockerScreen(BaseDashboardScreen):
    BINDINGS = [
        ("s", "start_container", "Start"),
        ("x", "stop_container", "Stop"),
        ("r", "restart_container", "Restart"),
        ("d", "remove_container", "Delete"),
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
        v = row_key.value
        return None if v.startswith("project:") or v.startswith("spacer:") else v

    def _execute_action(self, action_func) -> None:
        container_id = self.get_selected_container_id()
        if container_id:
            action_func(container_id)
            self.query_one(DockerPanel).update_table()

    def action_start_container(self) -> None:
        self._execute_action(start_container)

    def action_stop_container(self) -> None:
        self._execute_action(stop_container)

    def action_restart_container(self) -> None:
        self._execute_action(restart_container)

    def action_remove_container(self) -> None:
        self._execute_action(remove_container)

    def action_refresh_containers(self) -> None:
        self.query_one(DockerPanel).update_table()
