#!/bin/bash
# ── DemBench Linux Build Script ──────────────────────────────────────
# Requires: Python 3.10+, pip install pyinstaller
# Output:   dist/DemBench (Linux ELF executable)

set -e

echo "[DemBench] Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "[DemBench] Building Linux executable..."
pyinstaller --onefile \
    --name DemBench \
    --windowed \
    --add-data "benchmarks:benchmarks" \
    --add-data "ui:ui" \
    --add-data "scoring.py:." \
    --add-data "reporter.py:." \
    --hidden-import=customtkinter \
    --hidden-import=psutil \
    --hidden-import=numpy \
    --hidden-import=pygame \
    --hidden-import=OpenGL \
    --hidden-import=OpenGL.GL \
    --hidden-import=OpenGL.GLU \
    --hidden-import=speedtest \
    --collect-all customtkinter \
    main.py

chmod +x dist/DemBench
echo "[DemBench] Build complete!"
echo "Output: dist/DemBench"
