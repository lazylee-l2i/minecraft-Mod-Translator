"""File and directory management utilities."""
from pathlib import Path
from typing import List

from ..config.constants import INPUT_MODS_DIR, RESULT_PACK_DIR, TRANSLATE_CACHE_DIR, LOGS_DIR, ASSETS_DIR
from .logger import get_logger
from .exceptions import ConfigurationError

logger = get_logger(__name__)


def ensure_directories() -> None:
    """
    Create required directories if they don't exist.
    
    Creates:
        - input_mods/
        - result_pack/
        - translate_cache/
        - logs/
        - assets/
    """
    directories = [
        INPUT_MODS_DIR,
        RESULT_PACK_DIR,
        TRANSLATE_CACHE_DIR,
        LOGS_DIR,
        ASSETS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {directory}")
    
    logger.info("All required directories are ready")


def get_jar_files() -> List[Path]:
    """
    Get all JAR files from input directory.
    
    Returns:
        List of Path objects for JAR files
        
    Raises:
        ConfigurationError: If no JAR files found
    """
    if not INPUT_MODS_DIR.exists():
        INPUT_MODS_DIR.mkdir(parents=True, exist_ok=True)
    
    jar_files = list(INPUT_MODS_DIR.glob("*.jar"))
    
    if not jar_files:
        logger.warning(f"No JAR files found in {INPUT_MODS_DIR}")
        return []
    
    logger.info(f"Found {len(jar_files)} JAR file(s)")
    return jar_files


def clean_temp_files(temp_dir: Path) -> None:
    """
    Clean up temporary files and directories.
    
    Args:
        temp_dir: Temporary directory to remove
    """
    import shutil
    
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up {temp_dir}: {e}")
