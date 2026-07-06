@echo off
setlocal
set PYTHONPATH=%~dp0apps\backend
"%~dp0.venv\Scripts\python.exe" "%~dp0apps\backend\cli.py" %*
