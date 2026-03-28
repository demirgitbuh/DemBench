"""CPU Benchmark: prime calculation, matrix multiplication, recursive Fibonacci."""

import time
import os
import concurrent.futures


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _prime_bench() -> int:
    """Count primes up to 50000."""
    return sum(1 for n in range(2, 50_001) if _is_prime(n))


def _matrix_multiply() -> None:
    """Multiply two 150x150 matrices using pure Python lists."""
    size = 150
    a = [[float(i * size + j) for j in range(size)] for i in range(size)]
    b = [[float(i * size + j) for j in range(size)] for i in range(size)]
    result = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            a_ik = a[i][k]
            for j in range(size):
                result[i][j] += a_ik * b[k][j]


def _fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return _fibonacci(n - 1) + _fibonacci(n - 2)


def _fib_bench() -> int:
    return _fibonacci(32)


def _single_core_workload(_=None) -> float:
    """Run all three tests and return elapsed time."""
    start = time.perf_counter()
    _prime_bench()
    _matrix_multiply()
    _fib_bench()
    return time.perf_counter() - start


# Reference time for a mid-range system (Ryzen 5 5600 single core ~ 2.5s)
REFERENCE_SINGLE = 2.5
REFERENCE_MULTI = 0.6  # ~2.5s / (6 cores * some overhead)


def _run_multicore(cores: int) -> float:
    """Run CPU-bound workload in separate processes for true multi-core execution."""
    # Cap process count to prevent overloading very high-core servers.
    workers = max(1, min(cores, 16))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_single_core_workload, i) for i in range(workers)]
        times = [future.result() for future in concurrent.futures.as_completed(futures)]
    # Wall-clock completion approximated by the slowest worker.
    return max(times)


def run(progress_callback=None) -> dict:
    """Run CPU benchmark and return results dict."""
    try:
        cores = os.cpu_count() or 4

        if progress_callback:
            progress_callback(0.1, "Running single-core test...")
        single_time = _single_core_workload()

        if progress_callback:
            progress_callback(0.4, "Running multi-core test...")

        try:
            multi_time = _run_multicore(cores)
        except Exception:
            # Fallback: ThreadPool still gives a result even if process spawning is unavailable.
            with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
                futures = [executor.submit(_single_core_workload, i) for i in range(cores)]
                times = [future.result() for future in concurrent.futures.as_completed(futures)]
            multi_time = max(times)

        if progress_callback:
            progress_callback(0.9, "Calculating scores...")

        single_score = int(min((REFERENCE_SINGLE / max(single_time, 0.001)) * 50_000, 100_000))
        multi_score = int(min((REFERENCE_MULTI / max(multi_time, 0.001)) * 50_000 * (min(cores, 16) / 6), 100_000))

        total_duration = single_time + multi_time

        if progress_callback:
            progress_callback(1.0, "CPU benchmark complete.")

        return {
            "single_core_score": single_score,
            "multi_core_score": multi_score,
            "duration_s": round(total_duration, 2),
        }
    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"CPU benchmark error: {e}")
        return {
            "single_core_score": 0,
            "multi_core_score": 0,
            "duration_s": 0.0,
        }
