"""Minecraft version to pack_format mapping."""
from typing import Optional

# Reference: https://minecraft.wiki/w/Pack_format
PACK_FORMAT_MAP: dict[str, int] = {
    # 1.18.x
    "1.18": 8, "1.18.1": 8, "1.18.2": 8,
    # 1.19.x
    "1.19": 9, "1.19.1": 9, "1.19.2": 9,
    "1.19.3": 12,
    "1.19.4": 13,
    # 1.20.x
    "1.20": 15, "1.20.1": 15,
    "1.20.2": 18,
    "1.20.3": 22, "1.20.4": 22,
    "1.20.5": 32, "1.20.6": 32,
    # 1.21.x
    "1.21": 34, "1.21.1": 34,
    "1.21.2": 42, "1.21.3": 42,
    "1.21.4": 46,
    "1.21.5": 55,
    "1.21.6": 63,
    "1.21.7": 64, "1.21.8": 64,
    "1.21.9": 69, "1.21.10": 69,
    "1.21.11": 75,
}


def get_pack_format(version: str) -> Optional[int]:
    """
    Get pack_format for a Minecraft version.
    
    Args:
        version: Minecraft version string (e.g., "1.21.4")
        
    Returns:
        pack_format integer or None if version not found
    """
    return PACK_FORMAT_MAP.get(version)


def get_supported_versions() -> list[str]:
    """
    Get list of supported Minecraft versions in descending order.
    
    Returns:
        List of version strings from newest to oldest
    """
    # Sort versions properly (convert to tuples of integers for comparison)
    def version_key(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split("."))
    
    return sorted(PACK_FORMAT_MAP.keys(), key=version_key, reverse=True)
