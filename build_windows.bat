@echo off
REM ── DemBench Windows Build Script ──────────────────────────────────
REM Requires: Python 3.10+, pip install pyinstaller
REM Output:   dist\DemBench.exe

echo [DemBench] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo [DemBench] Building Windows executable...
pyinstaller --onefile ^
    --name DemBench ^
    --windowed ^
    --icon=NUL ^
    --add-data "benchmarks;benchmarks" ^
    --add-data "ui;ui" ^
    --add-data "scoring.py;." ^
    --add-data "reporter.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=psutil ^
    --hidden-import=numpy ^
    --hidden-import=pygame ^
    --hidden-import=OpenGL ^
    --hidden-import=OpenGL.GL ^
    --hidden-import=OpenGL.GLU ^
    --hidden-import=speedtest ^
    --collect-all customtkinter ^
    main.py

echo [DemBench] Build complete!
echo Output: dist\DemBench.exe
pause
