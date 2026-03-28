# DemBench - DemirArch System Benchmark Tool

A terminal-based (TUI) system benchmark tool that tests CPU, RAM, Disk, GPU, and Network performance.

## Features

- **CPU Benchmark**: Single-core and multi-core testing (primes, matrix multiplication, Fibonacci)
- **RAM Benchmark**: Sequential read/write bandwidth measurement
- **Disk Benchmark**: Sequential read/write speed with 256 MB temp file
- **GPU Benchmark**: OpenGL triangle render loop (optional)
- **Network Benchmark**: Download/upload speed and ping via speedtest (optional)
- **Scoring**: Normalized 0–100,000 score per component with weighted total
- **TUI**: Live progress bars and results via Textual
- **JSON Report**: Detailed report saved automatically after each run

## Installation

```bash
# Clone or download the project
cd dembench

# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.10+
- Dependencies: textual, psutil, rich, numpy, PyOpenGL, pygame, speedtest-cli

## Usage

```bash
# Run full benchmark
python main.py

# Skip GPU test
python main.py --no-gpu

# Skip network test
python main.py --no-network

# Skip both and specify output path
python main.py --no-gpu --no-network --output my_report.json
```

### Controls

- **q** — Quit the application

## Scoring System

Each component generates a score from 0 to 100,000. The total score is a weighted average:

| Component | Weight |
|-----------|--------|
| CPU       | 30%    |
| RAM       | 20%    |
| Disk      | 20%    |
| GPU       | 20%    |
| Network   | 10%    |

Reference system: Ryzen 5 5600, 16 GB DDR4, NVMe SSD, mid-range GPU, 100 Mbps internet.

## Sample Output

```
  ____                  ____                  _
 |  _ \  ___ _ __ ___ | __ )  ___ _ __   ___| |__
 | | | |/ _ \ '_ ` _ \|  _ \ / _ \ '_ \ / __| '_ \
 | |_| |  __/ | | | | | |_) |  __/ | | | (__| | | |
 |____/ \___|_| |_| |_|____/ \___|_| |_|\___|_| |_|

        DemirArch  |  DemBench v1.0  |  System Benchmark Tool

  BENCHMARK RESULTS
  CPU Score:     45,230  (Single: 42,100 | Multi: 48,360)
  RAM Score:     38,500  (R: 12500 MB/s | W: 10200 MB/s)
  Disk Score:    62,100  (R: 2100 MB/s | W: 1800 MB/s)
  GPU Score:     55,000
  Network Score: 71,200  (DL: 85.3 Mbps | UL: 42.1 Mbps)

  TOTAL SCORE: 51,893 / 100,000
```

## JSON Report

A report file `dembench_report_YYYYMMDD_HHMMSS.json` is generated after each run:

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
├── benchmarks/
│   ├── __init__.py
│   ├── cpu.py           # CPU benchmark
│   ├── ram.py           # RAM benchmark
│   ├── disk.py          # Disk benchmark
│   ├── gpu.py           # GPU benchmark (OpenGL)
│   └── network.py       # Network benchmark (speedtest)
├── ui/
│   ├── __init__.py
│   ├── app.py           # Textual app
│   └── widgets.py       # Custom TUI widgets
├── scoring.py           # Score calculation
├── reporter.py          # JSON report generator
├── requirements.txt
├── README.md
└── LICENSE
```

## License

GPL-3.0 - See [LICENSE](LICENSE) for details.

**DemirArch** - DemBench v1.0
