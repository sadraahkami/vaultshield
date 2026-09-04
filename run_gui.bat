@echo off
title VaultShield - Privacy & Security Studio
echo Starting VaultShield Desktop GUI...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred. If PyQt6 is missing, run: pip install -r requirements.txt
    pause
)
