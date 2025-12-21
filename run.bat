@echo off
cd /d "%~dp0"
if not exist .venv (
    echo [Error] Virtual environment not found. Please run 'py -3.11 -m venv .venv' and install requirements.
    pause
    exit /b
)
call .venv\Scripts\activate
python run_interactive.py
if errorlevel 1 pause
