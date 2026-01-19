import PyInstaller.__main__
import shutil
import os
from pathlib import Path

def build():
    print("Building Minecraft Mod Translator...")
    
    # Ensure assets exist
    if not os.path.exists("assets/pack_icon.png"):
        print("Warning: assets/pack_icon.png not found. Icon will be missing.")

    # PyInstaller arguments
    args = [
        'run.py',                           # Entry point
        '--name=MinecraftModTranslator',    # Name of the executable
        '--onefile',                        # Single executable file
        '--windowed',                       # No console window (GUI)
        '--add-data=assets;assets',         # Include assets folder
        '--icon=assets/pack_icon.png',      # Icon file
        '--clean',                          # Clean cache
        '--noconfirm',                      # Overwrite output directory
        
        # Exclude unnecessary heavy libraries
        '--exclude-module=torch',
        '--exclude-module=tensorflow',
        '--exclude-module=tensorboard',
        '--exclude-module=pandas',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=sklearn',
        '--exclude-module=matplotlib',
        '--exclude-module=cv2',
        '--exclude-module=PIL',
        '--exclude-module=numba',
        '--exclude-module=llvmlite',
        '--exclude-module=notebook',
        '--exclude-module=ipython',
        '--exclude-module=zmq',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Create Release folder
    release_dir = Path("Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Move EXE to Release
    dist_exe = Path("dist/MinecraftModTranslator.exe")
    if dist_exe.exists():
        shutil.move(str(dist_exe), str(release_dir / "MinecraftModTranslator.exe"))
        print(f"Build successful! Executable moved to {release_dir / 'MinecraftModTranslator.exe'}")
    else:
        print("Build failed: Executable not found in dist/")
        return

    # Create necessary directories in Release for user convenience
    (release_dir / "input_mods").mkdir(exist_ok=True)
    (release_dir / "result_pack").mkdir(exist_ok=True)
    (release_dir / "translate_cache").mkdir(exist_ok=True)
    (release_dir / "logs").mkdir(exist_ok=True)
    
    print("Created default directories in Release/")
    print("Done!")

if __name__ == "__main__":
    build()
