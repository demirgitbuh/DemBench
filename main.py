#!/usr/bin/env python3
"""DemBench - DemirArch System Benchmark Tool

A GUI-based system benchmark tool that tests CPU, RAM, Disk, GPU, and Network
performance and generates a comprehensive JSON report.

License: GPL-3.0-or-later
"""

import argparse
import multiprocessing
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="dembench",
        description="DemBench v1.0 - DemirArch System Benchmark Tool",
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Skip GPU benchmark",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip network benchmark",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for JSON report (default: dembench_report_YYYYMMDD_HHMMSS.json)",
    )
    args = parser.parse_args()

    try:
        from ui.app import DemBenchApp

        app = DemBenchApp(
            skip_gpu=args.no_gpu,
            skip_network=args.no_network,
            output_path=args.output,
        )
        app.run()
    except Exception:
        import traceback
        err = traceback.format_exc()
        print(err)
        with open("dembench_error.log", "w") as f:
            f.write(err)
        input("Press Enter to exit...")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
