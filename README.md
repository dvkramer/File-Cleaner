# Predictive File Cleaner

A Windows utility that helps you identify old files that may be candidates for deletion.

## Features

- Runs silently in the system tray
- Analyzes your Downloads folder for files older than 6 months
- Suggests files for potential deletion without moving or modifying them
- Displays notifications with examples of old files found
- Includes a "Check Now" option to scan on demand

## How It Works

The Predictive File Cleaner uses a simple but effective approach:

1. It scans your Downloads folder periodically (once per day)
2. Identifies files that haven't been modified or accessed in over 6 months
3. Displays a notification with the number of old files and a few examples
4. Leaves the decision to review and delete completely in your hands

The app doesn't delete any files automatically - it just provides helpful suggestions.

## Setup Options

### Option 1: Run as Python Script
1. Run the application by double-clicking `run_predictor.bat`
2. The app will run in your system tray with a green "P" icon
3. Right-click the icon to exit or manually trigger a scan

### Option 2: Create Standalone EXE
1. Run `run_create_exe.bat` to create a standalone executable
2. The EXE will be created in the `dist` folder
3. You can copy this EXE anywhere and run it without needing Python installed

## Requirements

- Windows 10 or later
- Python 3.6+ (only if running as script, not needed for EXE)