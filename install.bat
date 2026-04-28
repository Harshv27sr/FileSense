@echo off
echo Installing AI File Management System...
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python first.
    pause
    exit /b
)

echo Installing requirements...
pip install -r requirements.txt

echo.
echo Installation complete!
echo Run 'python main.py' to start the application
pause