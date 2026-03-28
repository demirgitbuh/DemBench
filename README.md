# DemBench — DemirArch System Benchmark Tool

A modern, Material Design 3 inspired desktop benchmark tool built with Python and CustomTkinter. Tests your system across 5 components and gives a unified score out of 100,000.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-GPL--3.0--or--later-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Brand](https://img.shields.io/badge/Brand-DemirArch-00D4AA)

## Features

- **CPU Benchmark** — Single-core & multi-core testing (prime calculation, matrix multiplication, recursive Fibonacci)
- **RAM Benchmark** — Sequential read/write bandwidth measurement via NumPy
- **Disk Benchmark** — Sequential read/write speed with 256 MB temp file (HDD & SSD compatible)
- **GPU Benchmark** — OpenGL triangle render loop via PyOpenGL + Pygame (auto-skips if unavailable)
- **Network Benchmark** — Download/upload speed & ping via speedtest-cli
- **Modern GUI** — Fullscreen Material Design 3 dark theme, animated progress bars, status chips, score tiers
- **JSON Report** — Auto-generated detailed report after each run
- **Error Resilient** — Never crashes; gracefully skips failed tests and continues

## Screenshots

```
  ____                  ____                  _
 |  _ \  ___ _ __ ___ | __ )  ___ _ __   ___| |__
 | | | |/ _ \ '_ ` _ \|  _ \ / _ \ '_ \ / __| '_ \
 | |_| |  __/ | | | | | |_) |  __/ | | | (__| | | |
 |____/ \___|_| |_| |_|____/ \___|_| |_|\___|_| |_|

        DemirArch  •  DemBench v1.0  •  System Benchmark
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/dembench.git
cd dembench
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- customtkinter, psutil, numpy, PyOpenGL, pygame, speedtest-cli, rich

## Usage

```bash
# Full benchmark
python main.py

# Skip GPU test
python main.py --no-gpu

# Skip network test
python main.py --no-network

# Custom output path
python main.py --no-gpu --no-network --output my_report.json
```

On Windows you can also double-click **`DemBench.bat`** to launch directly.

### Controls

| Key | Action |
|-----|--------|
| `Q` | Quit |
| `Escape` | Quit |

## Scoring System

Each component generates a normalized score from 0 to 100,000. The total score is a weighted average:

| Component | Weight | Test Method |
|-----------|--------|-------------|
| CPU | 30% | Primes, matrix multiplication, Fibonacci |
| RAM | 20% | NumPy array read/write bandwidth |
| Disk | 20% | 256 MB sequential read/write |
| GPU | 20% | OpenGL triangle render loop |
| Network | 10% | speedtest download/upload/ping |

**Reference system:** Ryzen 5 5600, 16 GB DDR4, NVMe SSD, mid-range GPU, 100 Mbps internet.

### Score Tiers

| Score | Tier |
|-------|------|
| 80,000+ | EXCELLENT |
| 60,000+ | GREAT |
| 40,000+ | GOOD |
| 20,000+ | AVERAGE |
| < 20,000 | LOW |

## JSON Report

A report file `dembench_report_YYYYMMDD_HHMMSS.json` is auto-generated after each run:

```json
{
  "tool": "DemBench",
  "version": "1.0.0",
  "brand": "DemirArch",
  "timestamp": "2026-03-28T14:30:00",
  "system": {
    "os": "Windows 11",
    "cpu": "AMD Ryzen 5 5600",
    "cpu_cores": 12,
    "ram_total_gb": 16.0,
    "python_version": "3.12.0"
  },
  "results": {
    "cpu": { "single_core_score": 42100, "multi_core_score": 48360, "duration_s": 5.2 },
    "ram": { "read_mbps": 12500.0, "write_mbps": 10200.0, "score": 38500 },
    "disk": { "read_mbps": 2100.0, "write_mbps": 1800.0, "score": 62100 },
    "gpu": { "score": 55000, "skipped": false },
    "network": { "download_mbps": 85.3, "upload_mbps": 42.1, "ping_ms": 12.5, "score": 71200, "skipped": false }
  },
  "total_score": 51893
}
```

## Project Structure

```
dembench/
├── main.py              # Entry point with CLI args
├── DemBench.bat         # Windows launcher
├── benchmarks/
│   ├── cpu.py           # CPU benchmark
│   ├── ram.py           # RAM benchmark
│   ├── disk.py          # Disk benchmark
│   ├── gpu.py           # GPU benchmark (OpenGL)
│   └── network.py       # Network benchmark (speedtest)
├── ui/
│   ├── app.py           # CustomTkinter GUI (Material Design 3)
│   └── widgets.py       # Theme constants
├── scoring.py           # Weighted score calculation
├── reporter.py          # JSON report generator
├── requirements.txt
├── LICENSE              # GPL-3.0-or-later
└── .gitignore
```

## License

GPL-3.0-or-later — See [LICENSE](LICENSE) for details.

---

**DemirArch** — DemBench v1.0
