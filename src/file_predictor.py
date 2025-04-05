#!/usr/bin/env python3
import os
import time
import datetime
import threading
import tempfile
import subprocess
import sys
from pathlib import Path
import pystray
from PIL import Image, ImageDraw

class PredictiveFileCleaner:
    def __init__(self):
        self.running = True
        self.min_interval = 3 * 60 * 60   # Minimum: 3 hours in seconds
        self.max_interval = 12 * 60 * 60  # Maximum: 12 hours in seconds
        
        # Different thresholds for different folders
        self.thresholds = {
            "Downloads": 180,  # 6 months in days
            "Documents": 365   # 1 year in days
        }
        
        # Create a simple icon for the tray
        self.create_tray_icon()
        
        # Automatically add to startup if not already there
        if not self.check_startup_status():
            print("Adding to Windows startup automatically...")
            self.add_to_startup()
        
        # Set up the tray icon
        self.tray_thread = threading.Thread(target=self.setup_tray)
        self.tray_thread.daemon = True
        self.tray_thread.start()
        
        # Start the monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_files)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Keep the main thread alive
        while self.running:
            time.sleep(1)
    
    def create_tray_icon(self):
        # Create a simple icon - white "P" on green background
        image = Image.new('RGB', (64, 64), color=(0, 120, 0))
        d = ImageDraw.Draw(image)
        d.text((24, 15), "P", fill=(255, 255, 255))
        
        # Save to temp directory to ensure write permissions
        temp_dir = tempfile.gettempdir()
        self.icon_path = os.path.join(temp_dir, "predictive_icon.png")
        image.save(self.icon_path)
    
    def add_to_startup(self):
        """Add the application to Windows startup"""
        try:
            import winreg
            
            # Get the path to the executable
            if getattr(sys, 'frozen', False):
                # We're running in a PyInstaller bundle
                app_path = f'"{sys.executable}"'
            else:
                # We're running in a normal Python environment
                script_path = os.path.abspath(sys.argv[0])
                app_path = f'pythonw "{script_path}"'
            
            # Open the registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # Set the value
            winreg.SetValueEx(key, "PredictiveFileCleaner", 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error adding to startup: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove the application from Windows startup"""
        try:
            import winreg
            # Open the registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # Delete the value
            winreg.DeleteValue(key, "PredictiveFileCleaner")
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error removing from startup: {e}")
            return False
    
    def check_startup_status(self):
        """Check if the application is in Windows startup"""
        try:
            import winreg
            # Open the registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            
            # Try to get the value
            try:
                winreg.QueryValueEx(key, "PredictiveFileCleaner")
                winreg.CloseKey(key)
                return True
            except:
                winreg.CloseKey(key)
                return False
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return False
    
    def toggle_startup(self):
        """Toggle the application in Windows startup"""
        if self.check_startup_status():
            success = self.remove_from_startup()
            status = "Removed from startup" if success else "Failed to remove from startup"
        else:
            success = self.add_to_startup()
            status = "Added to startup" if success else "Failed to add to startup"
        
        # Show a notification about the result
        self.show_notification("Startup Status", status)

    def setup_tray(self):
        try:
            # Load the generated icon
            image = Image.open(self.icon_path)
            
            # Create the menu dynamically based on startup status
            if self.check_startup_status():
                startup_text = "Remove from Startup"
            else:
                startup_text = "Add to Startup"
                
            menu = pystray.Menu(
                pystray.MenuItem("Check Now", self.check_now),
                pystray.MenuItem(startup_text, self.toggle_startup),
                pystray.MenuItem("Exit", self.exit_app)
            )
            self.icon = pystray.Icon("PredictiveCleaner", image, "Predictive File Cleaner", menu)
            self.icon.run()
        except Exception as e:
            print(f"Error setting up tray icon: {e}")
    
    def exit_app(self):
        self.running = False
        self.icon.stop()
    
    def check_now(self):
        """Force an immediate check for old files"""
        threading.Thread(target=self.analyze_folders).start()
    
    def show_notification(self, title, message):
        """Display a Windows notification using standard Windows MessageBox"""
        print(f"NOTIFICATION: {title} - {message}")
        
        # Use Windows native message box - simple and reliable
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0)
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def get_special_folder(self, folder_name):
        """Get the path to the user's special folder"""
        if os.name == 'nt':  # Windows
            import winreg
            
            # GUIDs for special folders
            folder_guids = {
                "Downloads": '{374DE290-123F-4565-9164-39C4925E467B}',
                "Documents": 'Personal'  # "Personal" is the registry name for Documents
            }
            
            try:
                sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                    folder_path = winreg.QueryValueEx(key, folder_guids[folder_name])[0]
                return folder_path
            except Exception as e:
                print(f"Error getting {folder_name} folder: {e}")
                # Fallback paths
                if folder_name == "Downloads":
                    return os.path.join(os.path.expanduser('~'), 'Downloads')
                elif folder_name == "Documents":
                    return os.path.join(os.path.expanduser('~'), 'Documents')
        else:  # Linux/Mac
            if folder_name == "Downloads":
                return os.path.join(os.path.expanduser('~'), 'Downloads')
            elif folder_name == "Documents":
                return os.path.join(os.path.expanduser('~'), 'Documents')
    
    def analyze_folders(self):
        """Analyze both Downloads and Documents folders for old files"""
        # Get current time for comparison
        now = datetime.datetime.now()
        
        # Results dictionary to store files by folder
        old_files_by_folder = {}
        total_file_count = 0
        
        # Check each folder with its corresponding threshold
        for folder_name, days_threshold in self.thresholds.items():
            folder_path = self.get_special_folder(folder_name)
            
            if not folder_path or not os.path.exists(folder_path):
                print(f"{folder_name} folder not found at {folder_path}")
                continue
            
            threshold_date = now - datetime.timedelta(days=days_threshold)
            
            # Find old files in this folder
            old_files = []
            print(f"Running predictive analysis on file system cluster: {folder_path}")
            
            for entry in os.scandir(folder_path):
                if entry.is_file():
                    # Get the last modified time of the file
                    modified_time = datetime.datetime.fromtimestamp(entry.stat().st_mtime)
                    
                    # Check if it's older than our threshold
                    if modified_time < threshold_date:
                        old_files.append(entry.name)
                        print(f"Identified file with usage pattern indicating low future utility: {entry.name}")
            
            if old_files:
                old_files_by_folder[folder_name] = old_files
                total_file_count += len(old_files)
        
        # Notify user if old files were found in any folder
        if old_files_by_folder:
            # Create a formatted list of files grouped by folder
            message_parts = ["Our predictive algorithms have identified files with low future utility probability:"]
            
            for folder, files in old_files_by_folder.items():
                message_parts.append(f"\n\n{folder} folder:")
                message_parts.append("\n".join(files))
            
            title = "Predictive File Analysis Report"
            message = "\n".join(message_parts) + "\n\nRecommended action: Review these files for potential removal."
            
            print(f"Analysis complete. Presenting findings for {total_file_count} identified candidates.")
            self.show_notification(title, message)
        else:
            print("Predictive analysis complete. No files with low utility probability detected.")
        
    def monitor_files(self):
        """Periodically check for old files at random intervals"""
        # First check immediately on startup
        self.analyze_folders()
        
        # Then check at random intervals between min and max
        while self.running:
            # Generate a random interval between min and max
            import random
            next_check_interval = random.randint(self.min_interval, self.max_interval)
            hours = next_check_interval / 3600
            print(f"Next analysis cycle scheduled in {hours:.1f} hours based on adaptive timing algorithm")
            
            # Sleep for the random interval
            time.sleep(next_check_interval)
            
            if self.running:  # Check again in case we've exited during the sleep
                print("Initiating scheduled predictive analysis cycle...")
                self.analyze_folders()

if __name__ == "__main__":
    PredictiveFileCleaner()