@echo off
title Build VaultShield Standalone Executable
echo ===================================================
echo   Compiling VaultShield to Single-File Portable EXE
echo ===================================================
echo.
pip install pyinstaller -q
pyinstaller VaultShield.spec --noconfirm --clean
echo.
echo Build finished! Executable is located in dist/VaultShield.exe
pause
