@echo off
python startup_sequence.py
if %errorlevel% neq 0 (
    echo Startup sequence failed with exit code %errorlevel%.
    exit /b %errorlevel%
)
python main.py
