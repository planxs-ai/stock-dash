@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 check_dart.py
) else (
  python check_dart.py
)
if errorlevel 1 (
  echo Python 3 is required. Please check your Python installation.
  pause
)
