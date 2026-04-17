from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Static

from pulse.services.system import get_active_processes, get_all_metrics
from pulse.ui.components.panels import create_panel
from pulse.ui.screens.base import BaseDashboardScreen

COLOR_DANGER = "#E53935"

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


class SystemMonitorPanel(Container):
    def compose(self) -> ComposeResult:
        yield SystemMetrics()
        yield ProcessTable()


class MonitorScreen(BaseDashboardScreen):
    def compose_panels(self) -> ComposeResult:
        yield create_panel(SystemMonitorPanel(), "Activity Monitor")
