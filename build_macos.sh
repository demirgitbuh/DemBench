#!/bin/bash
# ── DemBench macOS Build Script ──────────────────────────────────────
# Requires: Python 3.10+, pip install pyinstaller
# Output:   dist/DemBench.app (macOS application bundle)

set -e

echo "[DemBench] Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "[DemBench] Building macOS application..."
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
    --osx-bundle-identifier com.demirarch.dembench \
    main.py

echo "[DemBench] Build complete!"
echo "Output: dist/DemBench.app"

# Create DMG if create-dmg is available
if command -v create-dmg &> /dev/null; then
    echo "[DemBench] Creating DMG installer..."
    create-dmg \
        --volname "DemBench" \
        --window-size 600 400 \
        --icon-size 100 \
        --app-drop-link 400 200 \
        "dist/DemBench-v2.0-macOS.dmg" \
        "dist/DemBench.app"
    echo "DMG created: dist/DemBench-v2.0-macOS.dmg"
else
    echo "[INFO] Install 'create-dmg' for DMG packaging: brew install create-dmg"
fi
