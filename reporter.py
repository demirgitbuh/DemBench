"""JSON report generator."""

import json
import os
import platform
from datetime import datetime

import psutil

from scoring import compute_total_score


def generate_report(results: dict, output_path: str | None = None) -> str:
    """Generate a JSON benchmark report and write to file. Returns the file path."""
    total_score = compute_total_score(results)
    mem = psutil.virtual_memory()

    # Gather CPU model name
    cpu_name = platform.processor() or "Unknown"

    report = {
        "tool": "DemBench",
        "version": "1.0.0",
        "brand": "DemirArch",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": f"{platform.system()} {platform.release()}",
            "cpu": cpu_name,
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "python_version": platform.python_version(),
        },
        "results": {
            "cpu": {
                "single_core_score": results.get("cpu", {}).get("single_core_score", 0),
                "multi_core_score": results.get("cpu", {}).get("multi_core_score", 0),
                "duration_s": results.get("cpu", {}).get("duration_s", 0.0),
            },
            "ram": {
                "read_mbps": results.get("ram", {}).get("read_mbps", 0.0),
                "write_mbps": results.get("ram", {}).get("write_mbps", 0.0),
                "score": results.get("ram", {}).get("score", 0),
            },
            "disk": {
                "read_mbps": results.get("disk", {}).get("read_mbps", 0.0),
                "write_mbps": results.get("disk", {}).get("write_mbps", 0.0),
                "score": results.get("disk", {}).get("score", 0),
            },
            "gpu": {
                "score": results.get("gpu", {}).get("score", 0),
                "skipped": results.get("gpu", {}).get("skipped", False),
            },
            "network": {
                "download_mbps": results.get("network", {}).get("download_mbps", 0.0),
                "upload_mbps": results.get("network", {}).get("upload_mbps", 0.0),
                "ping_ms": results.get("network", {}).get("ping_ms", 0.0),
                "score": results.get("network", {}).get("score", 0),
                "skipped": results.get("network", {}).get("skipped", False),
            },
        },
        "total_score": total_score,
    }

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"dembench_report_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return os.path.abspath(output_path)
