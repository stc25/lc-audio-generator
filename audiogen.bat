@echo off
rem Windows CLI launcher: audiogen.bat <command> ...   (same commands as ./audiogen.sh)
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo First run: creating virtual environment... 1>&2
  py -3 -m venv .venv || python -m venv .venv
  .venv\Scripts\python -m pip install --upgrade pip -q
  .venv\Scripts\python -m pip install -r requirements.txt -q
)
.venv\Scripts\python -m audiogen %*
