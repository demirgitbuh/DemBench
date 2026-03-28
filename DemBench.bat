@echo off
title DemBench v1.0 - DemirArch
cd /d "%~dp0"
"C:\Users\demir\AppData\Local\Programs\Python\Python312\python.exe" main.py %*
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    pause
)
