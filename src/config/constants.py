"""Application constants and paths."""
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Directory paths
INPUT_MODS_DIR = BASE_DIR / "input_mods"
RESULT_PACK_DIR = BASE_DIR / "result_pack"
TRANSLATE_CACHE_DIR = BASE_DIR / "translate_cache"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Resource pack settings
PACK_DESCRIPTION = "번역기로 번역한 모드팩"
OUTPUT_FILENAME = "Translated_ResourcePack.zip"

# UI settings
WINDOW_TITLE = "Minecraft Mod Translator v2.0"
WINDOW_SIZE = "1100x1100"
MIN_WINDOW_SIZE = (1000, 1000)
