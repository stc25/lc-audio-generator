@echo off
rem Windows (PowerShell / cmd): creates a virtual environment on first run, then starts the UI.
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo First run: creating virtual environment...
  py -3 -m venv .venv || python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip -q
  .venv\Scripts\python -m pip install -r requirements.txt
)
where ffmpeg >nul 2>nul || echo note: ffmpeg not found. Install it with: winget install Gyan.FFmpeg
.venv\Scripts\python run.py %*
