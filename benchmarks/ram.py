"""RAM Benchmark: sequential read/write bandwidth using NumPy arrays."""

import time
import psutil
import numpy as np


# Reference bandwidth for DDR4-3200 ~ 20 GB/s practical
REFERENCE_WRITE_MBPS = 15_000.0
REFERENCE_READ_MBPS = 18_000.0
DEFAULT_BLOCK_SIZE_MB = 256
MIN_BLOCK_SIZE_MB = 64
MAX_BLOCK_SIZE_MB = 512


def run(progress_callback=None) -> dict:
    """Run RAM benchmark and return results dict."""
    try:
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024 ** 3), 2)
        available_gb = round(mem.available / (1024 ** 3), 2)

        # Use up to 10% of currently available memory to avoid OOM on low-memory systems.
        dynamic_block_mb = int((mem.available / (1024 ** 2)) * 0.10)
        block_mb = max(MIN_BLOCK_SIZE_MB, min(dynamic_block_mb, MAX_BLOCK_SIZE_MB, DEFAULT_BLOCK_SIZE_MB))
        block_bytes = block_mb * 1024 * 1024
        iterations = 3

        if progress_callback:
            progress_callback(0.1, "Measuring write bandwidth...")

        # Write benchmark: allocate and fill arrays
        write_times = []
        for i in range(iterations):
            src = np.random.randint(0, 256, size=block_bytes, dtype=np.uint8)
            start = time.perf_counter()
            dst = src.copy()
            write_times.append(time.perf_counter() - start)
            del src, dst
            if progress_callback:
                progress_callback(0.1 + 0.3 * (i + 1) / iterations, "Writing...")

        if progress_callback:
            progress_callback(0.5, "Measuring read bandwidth...")

        # Read benchmark: sequential access
        read_times = []
        data = np.random.randint(0, 256, size=block_bytes, dtype=np.uint8)
        for i in range(iterations):
            start = time.perf_counter()
            _ = data.sum()  # forces full sequential read
            read_times.append(time.perf_counter() - start)
            if progress_callback:
                progress_callback(0.5 + 0.4 * (i + 1) / iterations, "Reading...")
        del data

        avg_write = sum(write_times) / len(write_times)
        avg_read = sum(read_times) / len(read_times)

        write_mbps = round(block_mb / max(avg_write, 0.0001), 1)
        read_mbps = round(block_mb / max(avg_read, 0.0001), 1)

        # Score based on combined read/write performance
        write_ratio = min(write_mbps / REFERENCE_WRITE_MBPS, 1.0)
        read_ratio = min(read_mbps / REFERENCE_READ_MBPS, 1.0)
        score = int(((write_ratio + read_ratio) / 2) * 100_000)

        if progress_callback:
            progress_callback(1.0, "RAM benchmark complete.")

        return {
            "read_mbps": read_mbps,
            "write_mbps": write_mbps,
            "total_gb": total_gb,
            "available_gb": available_gb,
            "score": min(score, 100_000),
        }
    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"RAM benchmark error: {e}")
        return {
            "read_mbps": 0.0,
            "write_mbps": 0.0,
            "total_gb": 0.0,
            "available_gb": 0.0,
            "score": 0,
        }
