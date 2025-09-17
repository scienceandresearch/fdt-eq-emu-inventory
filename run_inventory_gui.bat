@echo off
echo ================================================================
echo    The Heroes Journey Inventory Manager
echo ================================================================
echo.
echo Checking Python installation...

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Could not install dependencies automatically
    echo You may need to run: pip install pandas
    echo.
)

echo.
echo Starting The Heroes Journey Inventory Manager...
echo.
python eq_inventory_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Could not start the application
    echo Try running: python eq_inventory_gui.py
    echo.
    pause
)
