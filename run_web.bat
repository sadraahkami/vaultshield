@echo off
title VaultShield - Web Studio
echo Starting VaultShield Web Server...
python main.py --web
if errorlevel 1 (
    echo.
    echo An error occurred while starting web server.
    pause
)
