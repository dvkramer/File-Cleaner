@echo off
echo Starting Predictive File Cleaner
echo Installing required packages if needed...
pip install pystray Pillow

echo Starting cleaner...
python %~dp0src\file_predictor.py
pause