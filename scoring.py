"""Scoring system: weighted average of component scores."""

# Weights for each component
WEIGHTS = {
    "cpu": 0.30,
    "ram": 0.20,
    "disk": 0.20,
    "gpu": 0.20,
    "network": 0.10,
}


def compute_cpu_combined_score(cpu_result: dict) -> int:
    """Average of single-core and multi-core scores."""
    s = cpu_result.get("single_core_score", 0)
    m = cpu_result.get("multi_core_score", 0)
    return (s + m) // 2


def compute_total_score(results: dict) -> int:
    """Compute weighted total score from all component results."""
    cpu_score = compute_cpu_combined_score(results.get("cpu", {}))
    ram_score = results.get("ram", {}).get("score", 0)
    disk_score = results.get("disk", {}).get("score", 0)
    gpu_score = results.get("gpu", {}).get("score", 0)
    network_score = results.get("network", {}).get("score", 0)

    total = (
        cpu_score * WEIGHTS["cpu"]
        + ram_score * WEIGHTS["ram"]
        + disk_score * WEIGHTS["disk"]
        + gpu_score * WEIGHTS["gpu"]
        + network_score * WEIGHTS["network"]
    )
    return int(min(total, 100_000))
