<!-- markdownlint-disable MD041 -->
<p align="center">
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/C.svg" width="60" alt="C"/>
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" width="60" alt="Python"/>
  <img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/GitHubActions-Dark.svg" width="60" alt="GitHub Actions"/>
</p>

<h1 align="center">🚴 Bike Maintenance Tracker</h1>

<p align="center">
  <em>Keep your road bike in race‑day shape – from the terminal or a futuristic dashboard</em>
</p>

<p align="center">
  <!-- CI/CD & Build -->
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/actions/workflows/ci.yml">
    <img src="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/actions/workflows/ci.yml/badge.svg" alt="CI/CD Pipeline"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/ci.yml?branch=master&style=flat-square&logo=githubactions&label=build" alt="Build Status"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/actions/workflows/codeql.yml">
    <img src="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/actions/workflows/codeql.yml/badge.svg" alt="CodeQL"/>
  </a>
</p>

<p align="center">
  <!-- Release & Versioning -->
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/releases">
    <img src="https://img.shields.io/github/v/release/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?include_prereleases&style=flat-square&logo=github" alt="GitHub release"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/tags">
    <img src="https://img.shields.io/github/v/tag/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="GitHub tag"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/commits">
    <img src="https://img.shields.io/github/last-commit/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="Last Commit"/>
  </a>
</p>

<p align="center">
  <!-- Repo Stats -->
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/stargazers">
    <img src="https://img.shields.io/github/stars/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="Stars"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/network">
    <img src="https://img.shields.io/github/forks/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="Forks"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/issues">
    <img src="https://img.shields.io/github/issues/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="Issues"/>
  </a>
  <a href="https://github.com/FrancescoCastaldi/Bike-Maintenance-Tracker-Application/pulls">
    <img src="https://img.shields.io/github/issues-pr/FrancescoCastaldi/Bike-Maintenance-Tracker-Application?style=flat-square" alt="Pull Requests"/>
  </a>
</p>

<p align="center">
  <!-- Code Quality -->
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="code style: black"/>
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit" alt="pre-commit"/>
  </a>
  <!-- License -->
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT"/>
  </a>
</p>

<p align="center">
  <!-- Tech Stack -->
  <img src="https://img.shields.io/badge/C-11-00599C?style=flat-square&logo=c&logoColor=white" alt="C11"/>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey?style=flat-square" alt="Platform"/>
</p>

---

## 📖 Overview

**Bike Maintenance Tracker** is a dual‑interface tool for cyclists who demand precision.  
It offers:

- a lightweight, blazing‑fast **C command‑line interface** for scripting and minimal environments,
- a modern **Python desktop dashboard** (powered by `ttkbootstrap` + `matplotlib`) that reads the same data files,
  giving you instant visual feedback on component wear and service history.

Every record is stored in human‑readable text files (`records.txt` and `components.txt`), so you can sync, version, or even hand‑edit them without lock‑in.

---

## 🧱 Repository Architecture

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml                  # Continuous Integration & Delivery
├── src/
│   ├── bike_track.c                # Core C application
│   └── bike_maintenance_gui.py     # Python GUI (ttkbootstrap + matplotlib)
├── requirements.txt                # Python dependencies
├── run.ps1                         # PowerShell build & run helper
├── run_gui.bat                     # Windows GUI quick‑start script
├── components.txt                  # Persisted component wear data
├── records.txt                     # Persisted maintenance records
└── README.md
```

> **CI Philosophy**  
> Each push triggers a matrix build on `ubuntu-latest`, `windows-latest`, and `macos-latest`:
> - C binary is compiled with both `gcc` and `clang`, then smoke‑tested.
> - Python environment is created, dependencies installed, and GUI smoketest is executed (headless Xvfb on Linux).
> - Code quality gates: `clang-format` check, `pylint`, and `shellcheck` on helper scripts.

The workflow file is thoroughly commented – you can use it as a reference for your own C+Python monorepos.

---

## ✨ Features

### 🔧 Maintenance Records Management
- Add, list, and search service records (date + description).
- Quick‑entry panel in the GUI for lightning‑fast logging.

### ⚖️ Bike Weight Tracking
- Store the current weight; view it at a glance in the dashboard.

### 🛡️ Component Wear Monitoring
- Track wear of tyres, inner tubes, derailleur cables, brake cables, bar tape.
- Colour‑coded wear bars and a diagnostic chart (matplotlib) highlight components that need immediate attention.

### 🌐 Futuristic Dashboard (Python GUI)
- Tech‑styled header with neon palette, animated status indicator.
- Summary cards (last service, total records, critical components) refreshed in real time.
- Diagnostics tab with live wear chart and automated maintenance suggestions.

### 🖥️ C Command‑Line Interface
- Ultra‑fast, dependency‑free (C standard library only).
- Ideal for CI pipelines, SSH sessions, or resource‑constrained devices.

---

## 🚀 Quick Start

### 🐍 Python GUI (all platforms)

```bash
# Create & activate virtual environment
python -m venv .venv-gui
source .venv-gui/bin/activate      # Windows: .venv-gui\Scripts\activate

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Launch the dashboard
python src/bike_maintenance_gui.py
```

**Windows one‑click:** Double‑click `run_gui.bat` or run it from a terminal; it will bootstrap the venv automatically.

### ⚙️ C Command‑Line Interface

#### Windows (PowerShell)
```powershell
# Ensure gcc or clang is in PATH, then:
./run.ps1            # incremental build & run
./run.ps1 -Clean     # force full rebuild
```

#### Linux / macOS
```bash
# Compile with gcc (or clang)
gcc -std=c11 -Wall -Wextra -O2 -o bike_track src/bike_track.c
./bike_track
```

---

## 📊 Component Wear Graph (example)

<p align="center">
  <img src="https://user-images.githubusercontent.com/placeholder/diagnostics-screenshot.png" width="600" alt="Diagnostics chart"/>
</p>

> The screenshot shows a sample *Diagnostics* tab: a radar/bar chart of component wear percentages, a critical‑parts list, and instant "replace now" or "monitor" suggestions.

---

## 🤝 Contributing

1. Fork the repository and create a feature branch.
2. Ensure the CI passes on your branch (`gcc`/`clang` compilation, Python lint, etc.).
3. Write or update tests if applicable (we use C unit tests with `check` and `pytest` for Python components).
4. Submit a pull request with a clear description.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. (File coming soon – PRs welcome!)

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for full text.

<p align="center">
  <sub>Built with ❤️ by cycling enthusiasts, for cycling enthusiasts.</sub>
</p>
