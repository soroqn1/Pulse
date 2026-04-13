from textual.app import App, ComposeResult
from textual.widgets import Static

from pulse.metrics import get_all_metrics


class SystemMetrics(Static):
    def on_mount(self) -> None:
        self.update_metrics()
        self.set_interval(1, self.update_metrics)

    def update_metrics(self) -> None:
        data = get_all_metrics()

        cpu = data["cpu_usage"]
        mem = data["memory_usage"]
        mem_used = mem["used"] / (1024**3)
        mem_total = mem["total"] / (1024**3)

        vidget_stat = f"CPU: {cpu:.1f}%\nRAM: {mem_used:.1f} / {mem_total:.1f} GB ({mem['percent']}%)"

        self.update(vidget_stat)


class PulseApp(App):
    def compose(self) -> ComposeResult:
        yield SystemMetrics()


if __name__ == "__main__":
    app = PulseApp()
    app.run()
