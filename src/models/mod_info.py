"""Mod information model."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModInfo:
    """
    Information about a mod extracted from JAR.
    
    Attributes:
        mod_id: Unique mod identifier
        version: Mod version string
        name: Human-readable mod name
        jar_path: Path to the original JAR file
    """
    mod_id: str
    version: str
    name: str
    jar_path: Path
    
    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self.name} ({self.mod_id}) v{self.version}"
    
    @property
    def display_name(self) -> str:
        """Get display name for UI."""
        return f"{self.name} v{self.version}"
