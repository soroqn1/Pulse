import math
import time

from rich.text import Text
from textual.widgets import Static


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
