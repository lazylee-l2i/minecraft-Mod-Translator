"""Application constants and paths."""
import sys
from pathlib import Path

# Base directory (project root)
if getattr(sys, 'frozen', False):
    # If frozen (PyInstaller), BASE_DIR is where the exe is
    BASE_DIR = Path(sys.executable).parent
    
    # Internal assets are in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        ASSETS_DIR = Path(sys._MEIPASS) / "assets"
    else:
        ASSETS_DIR = BASE_DIR / "assets"
else:
    # If running from source
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    ASSETS_DIR = BASE_DIR / "assets"

# Directory paths for user data
INPUT_MODS_DIR = BASE_DIR / "input_mods"
RESULT_PACK_DIR = BASE_DIR / "result_pack"
TRANSLATE_CACHE_DIR = BASE_DIR / "translate_cache"
LOGS_DIR = BASE_DIR / "logs"

# Resource pack settings
PACK_DESCRIPTION = "번역기로 번역한 모드팩"
OUTPUT_FILENAME = "Translated_ResourcePack.zip"

# UI settings
WINDOW_TITLE = "Minecraft Mod Translator v2.0"
WINDOW_SIZE = "1100x1100"
MIN_WINDOW_SIZE = (1000, 1000)
