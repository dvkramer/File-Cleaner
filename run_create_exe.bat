@echo off
echo Installing required packages for compilation...
pip install pyinstaller pystray Pillow

echo Creating standalone executable...
python "%~dp0create_exe.py"

if exist "%~dp0dist\PredictiveFileCleaner.exe" (
    echo.
    echo SUCCESS! Executable created at:
    echo %~dp0dist\PredictiveFileCleaner.exe
    echo.
    echo Double-click the EXE to run the Predictive File Cleaner.
) else (
    echo.
    echo ERROR: Something went wrong during compilation.
    echo Check the output above for errors.
)

pause