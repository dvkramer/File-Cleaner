import PyInstaller.__main__
import os
import shutil

# Get the current directory
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")
dist_dir = os.path.join(base_dir, "dist")
build_dir = os.path.join(base_dir, "build")

# Clean previous builds
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

# Set PyInstaller arguments
args = [
    src_dir + '/file_predictor.py',
    '--name=PredictiveFileCleaner',
    '--onefile',
    '--windowed',
]

print("Building executable...")
PyInstaller.__main__.run(args)
print(f"Executable created in {dist_dir}")

# Create a shortcut batch file that launches the EXE
shortcut_path = os.path.join(base_dir, "Run Predictor.bat")
with open(shortcut_path, "w") as f:
    f.write(f'@echo off\nstart "" "{os.path.join(dist_dir, "PredictiveFileCleaner.exe")}"\n')