"""Resource pack generation for translated mods."""
import json
import shutil
import zipfile
from pathlib import Path
from typing import Iterable, Optional

from ..config.constants import RESULT_PACK_DIR, ASSETS_DIR, PACK_DESCRIPTION, OUTPUT_FILENAME
from ..config.pack_formats import get_pack_format
from ..models.translation_data import TranslationResult
from ..utils.logger import get_logger
from ..utils.exceptions import ResourcePackError

logger = get_logger(__name__)


def build_resource_pack(
    translations: Iterable[TranslationResult],
    mc_version: str,
    output_dir: Optional[Path] = None,
    output_name: Optional[str] = None,
) -> Path:
    """
    Build a resource pack from translated language files.
    
    Args:
        translations: Iterable of translation results
        mc_version: Minecraft version for pack_format
        output_dir: Output directory (default: result_pack/)
        output_name: Output filename (default: Translated_ResourcePack.zip)
        
    Returns:
        Path to the generated resource pack ZIP file
        
    Raises:
        ResourcePackError: If generation fails
    """
    output_dir = output_dir or RESULT_PACK_DIR
    output_name = output_name or OUTPUT_FILENAME
    
    pack_format = get_pack_format(mc_version)
    if pack_format is None:
        raise ResourcePackError(f"Unsupported Minecraft version: {mc_version}")
    
    logger.info(f"Building resource pack for MC {mc_version} (pack_format: {pack_format})")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary directory for pack contents
    temp_dir = output_dir / "_temp_pack"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        translations_list = list(translations)
        
        if not translations_list:
            logger.warning("No translations to include in resource pack")
            raise ResourcePackError("No translations available")
        
        # Create pack structure
        _create_pack_structure(temp_dir, translations_list)
        
        # Create pack.mcmeta
        _create_pack_mcmeta(temp_dir, pack_format)
        
        # Copy pack icon
        _copy_pack_icon(temp_dir)
        
        # Create ZIP file
        output_path = output_dir / output_name
        _create_zip(temp_dir, output_path)
        
        logger.info(f"Resource pack created: {output_path}")
        logger.info(f"Included {len(translations_list)} mod translation(s)")
        
        return output_path
        
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def _create_pack_structure(
    temp_dir: Path, 
    translations: list[TranslationResult]
) -> None:
    """
    Create assets folder structure with translations.
    
    Args:
        temp_dir: Temporary directory for pack contents
        translations: List of translation results
    """
    assets_dir = temp_dir / "assets"
    
    for translation in translations:
        # Create mod language directory
        lang_dir = assets_dir / translation.mod_id / "lang"
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # Write ko_kr.json
        ko_kr_path = lang_dir / "ko_kr.json"
        with ko_kr_path.open("w", encoding="utf-8") as f:
            json.dump(
                translation.translated_content,
                f,
                ensure_ascii=False,
                indent=2
            )
        
        logger.debug(f"Created: {translation.lang_path}")


def _create_pack_mcmeta(temp_dir: Path, pack_format: int) -> None:
    """
    Generate pack.mcmeta file.
    
    Args:
        temp_dir: Temporary directory for pack contents
        pack_format: Minecraft pack format number
    """
    mcmeta_content = {
        "pack": {
            "description": PACK_DESCRIPTION,
            "pack_format": pack_format
        }
    }
    
    mcmeta_path = temp_dir / "pack.mcmeta"
    with mcmeta_path.open("w", encoding="utf-8") as f:
        json.dump(mcmeta_content, f, ensure_ascii=False, indent=2)
    
    logger.debug("Created pack.mcmeta")


def _copy_pack_icon(temp_dir: Path) -> None:
    """
    Copy pack icon to resource pack.
    
    Args:
        temp_dir: Temporary directory for pack contents
    """
    source_icon = ASSETS_DIR / "pack_icon.png"
    dest_icon = temp_dir / "pack.png"
    
    if source_icon.exists():
        shutil.copy2(source_icon, dest_icon)
        logger.debug("Copied pack.png")
    else:
        logger.warning("pack_icon.png not found, resource pack will have no icon")


def _create_zip(source_dir: Path, output_path: Path) -> None:
    """
    Create ZIP file from directory contents.
    
    Args:
        source_dir: Directory containing pack contents
        output_path: Output ZIP file path
    """
    # Remove existing file if present
    if output_path.exists():
        output_path.unlink()
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir)
                zf.write(file_path, arcname)
    
    logger.debug(f"Created ZIP: {output_path}")


def get_pack_info(pack_path: Path) -> Optional[dict]:
    """
    Read pack information from an existing resource pack.
    
    Args:
        pack_path: Path to the resource pack ZIP
        
    Returns:
        Dictionary with pack info or None if invalid
    """
    try:
        with zipfile.ZipFile(pack_path, 'r') as zf:
            if 'pack.mcmeta' in zf.namelist():
                with zf.open('pack.mcmeta') as f:
                    return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read pack info: {e}")
    return None
