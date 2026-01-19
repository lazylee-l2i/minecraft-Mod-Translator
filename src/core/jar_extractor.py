"""JAR file extraction and mod information discovery."""
import json
import re
import zipfile
from pathlib import Path
from typing import Generator, Optional, Tuple

from ..models.mod_info import ModInfo
from ..models.translation_data import LanguageFile
from ..utils.logger import get_logger
from ..utils.exceptions import JarExtractionError

logger = get_logger(__name__)


def extract_mod_info(jar_path: Path) -> Optional[ModInfo]:
    """
    Extract mod information from JAR file.
    
    Reads fabric.mod.json or mods.toml to get mod_id and version.
    
    Args:
        jar_path: Path to the JAR file
        
    Returns:
        ModInfo object or None if extraction fails
    """
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # Try Fabric mod (fabric.mod.json)
            if 'fabric.mod.json' in jar.namelist():
                try:
                    with jar.open('fabric.mod.json') as f:
                        data = json.load(f)
                        return ModInfo(
                            mod_id=data.get('id', jar_path.stem),
                            version=data.get('version', 'unknown'),
                            name=data.get('name', jar_path.stem),
                            jar_path=jar_path
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse fabric.mod.json: {e}")
            
            # Try Forge mod (META-INF/mods.toml)
            toml_path = 'META-INF/mods.toml'
            if toml_path in jar.namelist():
                try:
                    with jar.open(toml_path) as f:
                        content = f.read().decode('utf-8')
                        mod_id = _parse_toml_value(content, 'modId')
                        version = _parse_toml_value(content, 'version')
                        display_name = _parse_toml_value(content, 'displayName')
                        
                        # Handle ${file.jarVersion} placeholder
                        if version and version.startswith("${"):
                            version = _get_manifest_version(jar) or 'unknown'
                        
                        return ModInfo(
                            mod_id=mod_id or jar_path.stem,
                            version=version or 'unknown',
                            name=display_name or jar_path.stem,
                            jar_path=jar_path
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse mods.toml: {e}")
            
            # Try NeoForge/Quilt (neoforge.mods.toml, quilt.mod.json)
            for alt_path in ['META-INF/neoforge.mods.toml', 'quilt.mod.json']:
                if alt_path in jar.namelist():
                    logger.debug(f"Found alternative mod file: {alt_path}")
                    # Similar parsing logic...
        
        # Fallback: use filename
        logger.info(f"Using filename as mod info: {jar_path.stem}")
        return ModInfo(
            mod_id=jar_path.stem,
            version='unknown',
            name=jar_path.stem,
            jar_path=jar_path
        )
        
    except zipfile.BadZipFile:
        logger.error(f"Invalid JAR file: {jar_path}")
        return None
    except Exception as e:
        logger.warning(f"Failed to extract mod info from {jar_path}: {e}")
        return None


def extract_language_files(jar_path: Path) -> Generator[LanguageFile, None, None]:
    """
    Extract en_us.json files from a JAR file.
    
    Args:
        jar_path: Path to the JAR file
        
    Yields:
        LanguageFile objects containing mod info and content
    """
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                # Match assets/{mod_id}/lang/en_us.json pattern
                if name.endswith('en_us.json') and '/lang/' in name:
                    parts = name.split('/')
                    
                    # Validate path structure
                    if len(parts) >= 4 and parts[0] == 'assets':
                        mod_id = parts[1]
                        
                        try:
                            with jar.open(name) as f:
                                content = json.load(f)
                                
                                if content:  # Skip empty files
                                    logger.debug(f"Found language file: {name} ({len(content)} entries)")
                                    yield LanguageFile(
                                        mod_id=mod_id,
                                        content=content,
                                        original_path=Path(name)
                                    )
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON in {name}: {e}")
                        except Exception as e:
                            logger.warning(f"Failed to read {name}: {e}")
                            
    except zipfile.BadZipFile:
        logger.error(f"Invalid JAR file: {jar_path}")
        raise JarExtractionError(f"Invalid JAR file: {jar_path}")
    except Exception as e:
        logger.error(f"Failed to extract from {jar_path}: {e}")
        raise JarExtractionError(f"Extraction failed: {e}")


def get_language_file_count(jar_path: Path) -> int:
    """
    Count the number of language files in a JAR.
    
    Args:
        jar_path: Path to the JAR file
        
    Returns:
        Number of en_us.json files found
    """
    count = 0
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                if name.endswith('en_us.json') and '/lang/' in name:
                    count += 1
    except Exception:
        pass
    return count


def has_korean_translation(jar_path: Path, mod_id: str = "") -> bool:
    """
    Check if the JAR file already contains Korean translation (ko_kr.json).
    
    Args:
        jar_path: Path to the JAR file
        mod_id: Optional mod_id to check specific path
        
    Returns:
        True if ko_kr.json exists in the JAR
    """
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                # Match assets/{mod_id}/lang/ko_kr.json pattern
                if name.endswith('ko_kr.json') and '/lang/' in name:
                    parts = name.split('/')
                    if len(parts) >= 4 and parts[0] == 'assets':
                        # If mod_id specified, check if it matches
                        if mod_id and parts[1] != mod_id:
                            continue
                        
                        # Verify it's not empty
                        try:
                            with jar.open(name) as f:
                                content = json.load(f)
                                if content and len(content) > 0:
                                    logger.info(f"Found existing ko_kr.json in {jar_path.name}: {name} ({len(content)} entries)")
                                    return True
                        except Exception:
                            pass
    except Exception as e:
        logger.warning(f"Failed to check Korean translation in {jar_path}: {e}")
    
    return False


def _parse_toml_value(content: str, key: str) -> Optional[str]:
    """
    Simple TOML value parser.
    
    Args:
        content: TOML file content
        key: Key to search for
        
    Returns:
        Value string or None if not found
    """
    # Match key = "value" or key = 'value'
    pattern = rf'{key}\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, content)
    return match.group(1) if match else None


def _get_manifest_version(jar: zipfile.ZipFile) -> Optional[str]:
    """
    Get version from MANIFEST.MF file.
    
    Args:
        jar: Open ZipFile object
        
    Returns:
        Version string or None
    """
    try:
        if 'META-INF/MANIFEST.MF' in jar.namelist():
            with jar.open('META-INF/MANIFEST.MF') as f:
                content = f.read().decode('utf-8')
                # Look for Implementation-Version or Specification-Version
                for line in content.split('\n'):
                    if 'Implementation-Version:' in line:
                        return line.split(':', 1)[1].strip()
                    if 'Specification-Version:' in line:
                        return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None
