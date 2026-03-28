"""GPU Benchmark: OpenGL triangle render loop via pygame + PyOpenGL.

Runs in a subprocess to avoid conflicts with tkinter's main loop.
"""

import subprocess
import sys
import json
import os

REFERENCE_FRAMES = 5000

GPU_WORKER_CODE = '''
import time, json, sys, os

# Suppress pygame welcome message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame
    from pygame.locals import OPENGL, DOUBLEBUF
    from OpenGL.GL import (
        glClear, glBegin, glEnd, glVertex3f, glColor3f,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_TRIANGLES,
        glClearColor, glViewport, glFlush, glGetString,
        GL_RENDERER, GL_VERSION,
    )

    pygame.init()
    screen = pygame.display.set_mode((128, 128), OPENGL | DOUBLEBUF)
    pygame.display.set_caption("DemBench GPU Test")

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glViewport(0, 0, 128, 128)

    renderer = "unknown"
    version = "unknown"
    try:
        r = glGetString(GL_RENDERER)
        v = glGetString(GL_VERSION)
        if r: renderer = r.decode()
        if v: version = v.decode()
    except:
        pass

    target_duration = 5.0
    frame_count = 0
    start = time.perf_counter()

    while (time.perf_counter() - start) < target_duration:
        for event in pygame.event.get():
            pass
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for _ in range(100):
            glBegin(GL_TRIANGLES)
            glColor3f(0.0, 0.83, 0.67)
            glVertex3f(0.0, 0.5, 0.0)
            glVertex3f(-0.5, -0.5, 0.0)
            glVertex3f(0.5, -0.5, 0.0)
            glEnd()
        glFlush()
        pygame.display.flip()
        frame_count += 1

    elapsed = time.perf_counter() - start
    pygame.quit()

    print(json.dumps({
        "ok": True,
        "frames": frame_count,
        "elapsed": round(elapsed, 2),
        "renderer": renderer,
        "version": version,
    }))

except Exception as e:
    print(json.dumps({"ok": False, "frames": 0, "error": str(e)}))
'''


def run(progress_callback=None, skip=False) -> dict:
    """Run GPU benchmark and return results dict."""
    if skip:
        if progress_callback:
            progress_callback(1.0, "GPU test skipped (--no-gpu).")
        return {"score": 0, "skipped": True}

    try:
        if progress_callback:
            progress_callback(0.1, "Launching GPU test...")

        env = os.environ.copy()
        env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

        result = subprocess.run(
            [sys.executable, "-c", GPU_WORKER_CODE],
            capture_output=True, text=True, timeout=30, env=env,
        )

        if progress_callback:
            progress_callback(0.85, "Processing GPU results...")

        # Find JSON line in output (skip pygame messages)
        data = None
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                data = json.loads(line)
                break

        if data is None:
            stderr_msg = result.stderr.strip()[:200] if result.stderr else "No output"
            raise RuntimeError(f"GPU worker failed: {stderr_msg}")

        if not data.get("ok"):
            raise RuntimeError(data.get("error", "GPU test failed"))

        frame_count = data["frames"]
        score = int(min((frame_count / REFERENCE_FRAMES) * 100_000, 100_000))

        renderer = data.get("renderer", "unknown")
        if progress_callback:
            progress_callback(1.0, f"GPU: {renderer}")

        return {
            "score": score,
            "skipped": False,
            "frames": frame_count,
            "renderer": renderer,
        }

    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"GPU test error: {e}")
        return {"score": 0, "skipped": True}
