from textual.widgets import Static


def create_panel(content: str | Static, title: str) -> Static:
    panel = Static(content) if isinstance(content, str) else content
    panel.add_class("panel")
    panel.border_title = title
    panel.border_subtitle = "Pulse"
    panel.border_subtitle_align = "right"
    return panel
