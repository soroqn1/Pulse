<div align="center">
  <h1>⚡️ Pulse</h1>
  <p><b>Keyboard-driven TUI system monitor and Docker dashboard.</b></p>
  <p><i>Inspired by tools like lazydocker and OrbStack, bringing a clean, grouped visual hierarchy straight to your terminal.</i></p>
  <br>
</div>

> *"If you just want to track CPU spikes, tools like **bpytop** are king. But if you are a backend dev who constantly needs to kill Docker networks, read container logs, and check RAM in one terminal tab - that's exactly why I built Pulse."*

## ✨ Features

- 🐳 **Smart Docker Dashboard:**
  - **Auto-Grouping:** Visually groups containers by their `com.docker.compose.project` (Compose folder) so you always know what belongs where.
  - **Dynamic Sorting:** Brings active (`running`) projects immediately to the top of your screen.
  - **Zero-Lag Asynchronous Logs:** Instantly updates container logs without locking up the UI thread when scrolling.
  - **Quick Manage:** One-key shortcuts to Start, Stop, Restart, and Delete containers.
- 💻 **System Monitor (Activity):** Real-time macOS telemetry, displaying CPU, RAM usage, and active system processes in an organized matrix.
- 🧹 **System Cleaner:** Rapid cleanup for cached artifacts, Docker dangling images, and redundant system dependencies.
- 🎨 **Premium Aesthetic:** Dark-mode "Latte & Red" coloring, completely eliminating visual noise and pointless emojis.

## 🚀 Installation

Pulse is distributed as a highly optimized, standalone executable. No python environment config needed.

### Using Homebrew (macOS)
The fastest and easiest way to install:

```bash
brew install soroqn1/tap/pulse
```

That's it! Now you can open any terminal and type `pulse`.

### From Source
If you prefer building it yourself via Poetry:
```bash
git clone https://github.com/soroqn1/Pulse.git
cd Pulse
poetry install
poetry run pulse
```

## ⌨️ How to use (Hotkeys)

Navigation in Pulse is fully keyboard-driven. Use mapping keys depending on your currently selected dashboard screen:

### Global (Navigation)
- `tab` : Switch between dashboard panels (Menu / Monitor / Docker / Cleaner).

### Docker Dashboard
Use arrow keys (`↑` / `↓`) to navigate between containers. Logs are fetched automatically in the background.

- `s` : Start container
- `x` : Stop container
- `r` : Restart container
- `d` : Delete container
- `f` : Refresh list

---
