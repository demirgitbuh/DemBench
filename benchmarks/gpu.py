"""GPU Benchmark: 3D animated OpenGL scene via pygame + PyOpenGL.

Runs in a subprocess to avoid conflicts with tkinter's main loop.
Renders a complex 3D scene with rotating objects, lighting, and perspective projection.
"""

import subprocess
import sys
import json
import os

REFERENCE_FRAMES = 3000  # More realistic reference for 3D workload

GPU_WORKER_CODE = r'''
import time, json, sys, os, math

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame
    from pygame.locals import OPENGL, DOUBLEBUF
    from OpenGL.GL import *
    from OpenGL.GLU import gluPerspective, gluLookAt, gluNewQuadric, gluSphere, gluCylinder

    pygame.init()
    screen = pygame.display.set_mode((512, 512), OPENGL | DOUBLEBUF)
    pygame.display.set_caption("DemBench GPU 3D Test")

    # ── OpenGL Setup ──────────────────────────────────────────────────────
    glClearColor(0.02, 0.02, 0.06, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Light 0 - Main directional light (warm white)
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 7.0, 0.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.15, 0.15, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.9, 0.85, 0.8, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    # Light 1 - Accent light (teal)
    glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 3.0, -5.0, 0.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.0, 0.6, 0.5, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.8, 0.7, 1.0])

    # Material
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 64.0)

    # Perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    renderer = "unknown"
    version  = "unknown"
    try:
        r = glGetString(GL_RENDERER)
        v = glGetString(GL_VERSION)
        if r: renderer = r.decode()
        if v: version  = v.decode()
    except Exception:
        pass

    # ── 3D Geometry helpers ───────────────────────────────────────────────
    def draw_cube(size=1.0):
        s = size / 2.0
        faces = [
            # front
            ([0, 0, 1],  [(-s,-s, s),( s,-s, s),( s, s, s),(-s, s, s)]),
            # back
            ([0, 0,-1],  [( s,-s,-s),(-s,-s,-s),(-s, s,-s),( s, s,-s)]),
            # top
            ([0, 1, 0],  [(-s, s, s),( s, s, s),( s, s,-s),(-s, s,-s)]),
            # bottom
            ([0,-1, 0],  [(-s,-s,-s),( s,-s,-s),( s,-s, s),(-s,-s, s)]),
            # right
            ([1, 0, 0],  [( s,-s, s),( s,-s,-s),( s, s,-s),( s, s, s)]),
            # left
            ([-1, 0, 0], [(-s,-s,-s),(-s,-s, s),(-s, s, s),(-s, s,-s)]),
        ]
        glBegin(GL_QUADS)
        for normal, verts in faces:
            glNormal3f(*normal)
            for v in verts:
                glVertex3f(*v)
        glEnd()

    def draw_torus(R=1.0, r=0.3, N=32, n=16):
        for i in range(N):
            theta1 = 2 * math.pi * i / N
            theta2 = 2 * math.pi * (i + 1) / N
            glBegin(GL_QUAD_STRIP)
            for j in range(n + 1):
                phi = 2 * math.pi * j / n
                for theta in [theta1, theta2]:
                    ct, st = math.cos(theta), math.sin(theta)
                    cp, sp = math.cos(phi), math.sin(phi)
                    x = (R + r * cp) * ct
                    y = (R + r * cp) * st
                    z = r * sp
                    nx = cp * ct
                    ny = cp * st
                    nz = sp
                    glNormal3f(nx, ny, nz)
                    glVertex3f(x, y, z)
            glEnd()

    def draw_grid(size=10, step=1.0):
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor4f(0.15, 0.2, 0.25, 0.5)
        half = size * step / 2.0
        i = -half
        while i <= half + 0.001:
            glVertex3f(i, -2.0, -half)
            glVertex3f(i, -2.0, half)
            glVertex3f(-half, -2.0, i)
            glVertex3f(half, -2.0, i)
            i += step
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_pyramid(size=1.0):
        s = size / 2.0
        h = size
        # base
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glVertex3f(-s, 0, -s)
        glVertex3f( s, 0, -s)
        glVertex3f( s, 0,  s)
        glVertex3f(-s, 0,  s)
        glEnd()
        # 4 triangular faces
        def face_normal(v0, v1, v2):
            ux, uy, uz = v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]
            vx, vy, vz = v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]
            nx = uy*vz - uz*vy
            ny = uz*vx - ux*vz
            nz = ux*vy - uy*vx
            l = max(math.sqrt(nx*nx + ny*ny + nz*nz), 1e-8)
            return nx/l, ny/l, nz/l
        apex = (0, h, 0)
        base_verts = [(-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)]
        glBegin(GL_TRIANGLES)
        for i in range(4):
            v0 = base_verts[i]
            v1 = base_verts[(i + 1) % 4]
            n = face_normal(v0, v1, apex)
            glNormal3f(*n)
            glVertex3f(*v0)
            glVertex3f(*v1)
            glVertex3f(*apex)
        glEnd()

    quad = gluNewQuadric()

    # ── Render Loop ───────────────────────────────────────────────────────
    target_duration = 5.0
    frame_count = 0
    start = time.perf_counter()

    while (time.perf_counter() - start) < target_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        elapsed = time.perf_counter() - start
        angle = elapsed * 45.0  # 45 deg/sec rotation

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Camera orbit
        cam_x = 8.0 * math.sin(elapsed * 0.3)
        cam_z = 8.0 * math.cos(elapsed * 0.3)
        gluLookAt(cam_x, 4.0, cam_z,  0, 0.5, 0,  0, 1, 0)

        # Grid floor
        draw_grid(12, 1.0)

        # ── Central rotating cube (teal) ──
        glPushMatrix()
        glRotatef(angle, 0.3, 1.0, 0.2)
        glColor3f(0.0, 0.83, 0.67)
        draw_cube(1.5)
        glPopMatrix()

        # ── Orbiting spheres ──
        for k in range(6):
            a = angle * 1.5 + k * 60
            ox = 3.5 * math.cos(math.radians(a))
            oz = 3.5 * math.sin(math.radians(a))
            oy = 0.8 * math.sin(elapsed * 2.0 + k)
            glPushMatrix()
            glTranslatef(ox, oy + 0.5, oz)
            hue_shift = (k / 6.0) * 360
            r_c = 0.5 + 0.5 * math.sin(math.radians(hue_shift))
            g_c = 0.5 + 0.5 * math.sin(math.radians(hue_shift + 120))
            b_c = 0.5 + 0.5 * math.sin(math.radians(hue_shift + 240))
            glColor3f(r_c, g_c, b_c)
            gluSphere(quad, 0.35, 24, 24)
            glPopMatrix()

        # ── Torus ring ──
        glPushMatrix()
        glTranslatef(0, 2.5, 0)
        glRotatef(angle * 0.7, 1.0, 0.0, 0.3)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.9, 0.75, 0.0)
        draw_torus(1.8, 0.2, 36, 18)
        glPopMatrix()

        # ── Corner pyramids ──
        for sx, sz in [(-4, -4), (4, -4), (-4, 4), (4, 4)]:
            glPushMatrix()
            glTranslatef(sx, -2.0, sz)
            local_angle = angle + sx * 10 + sz * 10
            glRotatef(local_angle * 0.5, 0, 1, 0)
            glColor3f(0.6, 0.2, 0.8)
            draw_pyramid(1.2)
            glPopMatrix()

        # ── Additional stress: small rotating cubes ring ──
        for i in range(12):
            a2 = angle * 2.0 + i * 30
            rx = 5.5 * math.cos(math.radians(a2))
            rz = 5.5 * math.sin(math.radians(a2))
            ry = 1.0 + 0.5 * math.sin(elapsed * 3.0 + i * 0.5)
            glPushMatrix()
            glTranslatef(rx, ry, rz)
            glRotatef(a2 * 2, 1, 1, 0)
            glColor3f(0.0, 0.5 + 0.3 * math.sin(i), 0.8)
            draw_cube(0.4)
            glPopMatrix()

        # ── Secondary torus ──
        glPushMatrix()
        glTranslatef(0, -0.5, 0)
        glRotatef(angle * -0.4, 0.0, 1.0, 0.0)
        glColor3f(0.2, 0.8, 0.9)
        draw_torus(3.0, 0.12, 48, 12)
        glPopMatrix()

        pygame.display.flip()
        frame_count += 1

    elapsed_final = time.perf_counter() - start
    pygame.quit()

    print(json.dumps({
        "ok": True,
        "frames": frame_count,
        "elapsed": round(elapsed_final, 2),
        "fps": round(frame_count / max(elapsed_final, 0.001), 1),
        "renderer": renderer,
        "version": version,
    }))

except Exception as e:
    import traceback
    print(json.dumps({"ok": False, "frames": 0, "error": str(e), "traceback": traceback.format_exc()}))
'''


def run(progress_callback=None, skip=False) -> dict:
    """Run 3D GPU benchmark and return results dict."""
    if skip:
        if progress_callback:
            progress_callback(1.0, "GPU test skipped (--no-gpu).")
        return {"score": 0, "skipped": True}

    try:
        if progress_callback:
            progress_callback(0.05, "Launching 3D GPU test...")

        env = os.environ.copy()
        env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

        # Progress simulation during subprocess
        import threading, time
        progress_done = threading.Event()

        def progress_ticker():
            t = 0.1
            while not progress_done.is_set() and t < 0.80:
                if progress_callback:
                    progress_callback(t, f"Rendering 3D scene... ({int(t*100)}%)")
                progress_done.wait(0.5)
                t += 0.07
        ticker = threading.Thread(target=progress_ticker, daemon=True)
        ticker.start()

        result = subprocess.run(
            [sys.executable, "-c", GPU_WORKER_CODE],
            capture_output=True, text=True, timeout=30, env=env,
        )

        progress_done.set()
        ticker.join(timeout=2)

        if progress_callback:
            progress_callback(0.90, "Processing 3D GPU results...")

        # Find JSON line in output (skip pygame messages)
        data = None
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    data = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue

        if data is None:
            stderr_msg = result.stderr.strip()[:300] if result.stderr else "No output"
            stdout_msg = result.stdout.strip()[:300] if result.stdout else ""
            raise RuntimeError(f"GPU worker failed — stderr: {stderr_msg} | stdout: {stdout_msg}")

        if not data.get("ok"):
            error_detail = data.get("error", "GPU test failed")
            raise RuntimeError(error_detail)

        frame_count = data["frames"]
        fps = data.get("fps", 0)
        score = int(min((frame_count / REFERENCE_FRAMES) * 100_000, 100_000))

        renderer = data.get("renderer", "unknown")
        if progress_callback:
            progress_callback(1.0, f"GPU: {renderer} — {fps:.0f} FPS")

        return {
            "score": score,
            "skipped": False,
            "frames": frame_count,
            "fps": fps,
            "renderer": renderer,
            "version": data.get("version", "unknown"),
        }

    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"GPU test error: {e}")
        return {"score": 0, "skipped": True, "error": str(e)}
