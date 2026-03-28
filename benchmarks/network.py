"""Network Benchmark: download/upload speed and ping via speedtest-cli."""


def run(progress_callback=None, skip=False) -> dict:
    """Run network benchmark and return results dict."""
    if skip:
        if progress_callback:
            progress_callback(1.0, "Network test skipped (--no-network).")
        return {
            "download_mbps": 0.0,
            "upload_mbps": 0.0,
            "ping_ms": 0.0,
            "score": 0,
            "skipped": True,
        }

    try:
        if progress_callback:
            progress_callback(0.05, "Finding best server...")

        import speedtest

        st = speedtest.Speedtest()
        st.get_best_server()

        if progress_callback:
            progress_callback(0.2, "Testing download speed...")

        st.download()

        if progress_callback:
            progress_callback(0.55, "Testing upload speed...")

        st.upload()

        if progress_callback:
            progress_callback(0.9, "Calculating network score...")

        results = st.results.dict()
        download_mbps = round(results["download"] / 1_000_000, 2)
        upload_mbps = round(results["upload"] / 1_000_000, 2)
        ping_ms = round(results["ping"], 1)

        # Reference: 100 Mbps down, 50 Mbps up, 20ms ping
        dl_ratio = min(download_mbps / 100.0, 1.0)
        ul_ratio = min(upload_mbps / 50.0, 1.0)
        ping_ratio = min(20.0 / max(ping_ms, 1.0), 1.0)
        score = int(((dl_ratio * 0.5) + (ul_ratio * 0.3) + (ping_ratio * 0.2)) * 100_000)

        if progress_callback:
            progress_callback(1.0, "Network benchmark complete.")

        return {
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "ping_ms": ping_ms,
            "score": min(score, 100_000),
            "skipped": False,
        }
    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"Network test failed: {e}")
        return {
            "download_mbps": 0.0,
            "upload_mbps": 0.0,
            "ping_ms": 0.0,
            "score": 0,
            "skipped": False,
        }
