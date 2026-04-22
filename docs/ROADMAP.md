# Pulse: Engineering Roadmap & Architecture

This document tracks our core technical goals, constraints, and architectural decisions, specifically focusing on the evolution of Pulse from a standard TUI dashboard into an intelligent, ML-driven anomaly detection layer.

## 🎯 The Core Mission Constraint
- **Target Footprint**: Entire application (TUI + Docker Client + ML Anomaly Detection) must NOT exceed **50MB** of RAM.
- **CPU Target**: Idle consumption must approach 0%.
- **Philosophy**: No bloat, no heavy polling loops. We aim for surgical precision and low-level system integrations.

---

## 🛠️ Phase 1: Event-Driven System Telemetry
*Insight: Polling `psutil` every 0.1s is fundamentally incompatible with our 50MB/0% CPU goals.*

### 1. Replacing Polling with `cgroups` Notifications
Instead of actively requesting memory metrics, we will configure the OS kernel to notify us.
- **How it works**: Use Linux `cgroups` (control groups) memory thresholds. We will set soft limits for watched containers.
- **Action**: The Python daemon will sleep until the kernel triggers an event threshold via `cgroup.event_control` or the newer `memory.events`. The thread wakes up only when an anomaly starts happening.

### 2. Low-Level /proc Parsing
For environments where `cgroups` events are not viable, we bypass heavy libraries.
- **Action**: Write highly optimized bare-metal parsers for `/proc/meminfo` and `/proc/stat` instead of loading large system instrumentation libraries.

---

## 🧠 Phase 2: Embedded Local Machine Learning
*Challenge: Python ML libraries (PyTorch/Tensorflow) easily consume 200MB+ just by importing them.*

### Option A: The ONNX Runtime approach
- Train the anomaly detection model offline (e.g., a lightweight Autoencoder or Isolation Forest for time-series memory data).
- Export the graph to `.onnx`.
- Run the inference in Pulse using only `onnxruntime`, which is incredibly fast and memory-efficient.

### Option B: The Rust FFI (PyO3) approach
If pure Python proves too bloated, we will extract the anomaly detection entirely to Rust.
- Build the math/ML watcher in Rust.
- Compile it to a native Python extension (using PyO3).
- **Pros**: Rust memory is strictly managed (no Python GC bloat); runs natively alongside the TUI.

---

## 🔮 Phase 3: Actionable Analytics
Once anomalies are detected efficiently:
1. Fire a notification inside the TUI via the `pulse` Event bus.
2. Provide one-click "Kill & Restart" for looping containers.
3. Keep anomalous log chunks attached to the crash report inside the CLI.
