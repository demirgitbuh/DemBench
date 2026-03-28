"""Disk Benchmark: sequential read/write speed with a 256 MB temp file."""

import os
import time
import tempfile


FILE_SIZE_MB = 256
FILE_SIZE_BYTES = FILE_SIZE_MB * 1024 * 1024
CHUNK_SIZE = 1024 * 1024  # 1 MB chunks

# Reference: NVMe SSD ~ 2000 MB/s write, 3000 MB/s read
REFERENCE_WRITE_MBPS = 2000.0
REFERENCE_READ_MBPS = 3000.0


def run(progress_callback=None) -> dict:
    """Run disk benchmark and return results dict."""
    tmp_path = None
    try:
        if progress_callback:
            progress_callback(0.05, "Preparing disk test...")

        tmp_fd, tmp_path = tempfile.mkstemp(prefix="dembench_", suffix=".tmp")
        os.close(tmp_fd)

        # Generate random data in memory first
        data_chunk = os.urandom(CHUNK_SIZE)
        total_chunks = FILE_SIZE_BYTES // CHUNK_SIZE

        # Write benchmark
        if progress_callback:
            progress_callback(0.1, "Writing 256 MB test file...")

        start = time.perf_counter()
        with open(tmp_path, "wb") as f:
            for i in range(total_chunks):
                f.write(data_chunk)
            f.flush()
            os.fsync(f.fileno())
        write_time = time.perf_counter() - start

        if progress_callback:
            progress_callback(0.5, "Reading 256 MB test file...")

        # Read benchmark
        start = time.perf_counter()
        with open(tmp_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
        read_time = time.perf_counter() - start

        write_mbps = round(FILE_SIZE_MB / max(write_time, 0.0001), 1)
        read_mbps = round(FILE_SIZE_MB / max(read_time, 0.0001), 1)

        write_ratio = min(write_mbps / REFERENCE_WRITE_MBPS, 1.0)
        read_ratio = min(read_mbps / REFERENCE_READ_MBPS, 1.0)
        score = int(((write_ratio + read_ratio) / 2) * 100_000)

        if progress_callback:
            progress_callback(1.0, "Disk benchmark complete.")

        return {
            "read_mbps": read_mbps,
            "write_mbps": write_mbps,
            "score": min(score, 100_000),
        }
    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"Disk benchmark error: {e}")
        return {
            "read_mbps": 0.0,
            "write_mbps": 0.0,
            "score": 0,
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
