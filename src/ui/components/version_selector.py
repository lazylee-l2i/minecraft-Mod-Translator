"""Minecraft version selector dropdown."""
import tkinter as tk
from tkinter import ttk

from ..styles import Spacing
from ...config.pack_formats import get_supported_versions, get_pack_format


class VersionSelector(ttk.LabelFrame):
    """
    Dropdown selector for Minecraft version.
    
    Displays all supported versions and shows the corresponding pack_format.
    """
    
    DEFAULT_VERSION = "1.21.4"
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize version selector.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="마인크래프트 버전", padding=Spacing.MD)
        
        self._setup_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Initialize pack_format display
        self._update_pack_format()
    
    def _setup_widgets(self) -> None:
        """Create panel widgets."""
        # Version label
        self.version_label = ttk.Label(self, text="버전 선택:")
        
        # Version dropdown
        self.version_var = tk.StringVar(value=self.DEFAULT_VERSION)
        versions = get_supported_versions()
        
        self.version_combo = ttk.Combobox(
            self,
            textvariable=self.version_var,
            values=versions,
            state="readonly",
            width=12
        )
        
        # Pack format display
        self.format_label = ttk.Label(self, text="")
    
    def _setup_layout(self) -> None:
        """Arrange widgets."""
        self.version_label.pack(side=tk.LEFT, padx=Spacing.SM)
        self.version_combo.pack(side=tk.LEFT, padx=Spacing.SM)
        self.format_label.pack(side=tk.LEFT, padx=Spacing.MD)
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.version_combo.bind("<<ComboboxSelected>>", self._on_version_change)
    
    def _on_version_change(self, event=None) -> None:
        """Handle version selection change."""
        self._update_pack_format()
    
    def _update_pack_format(self) -> None:
        """Update pack_format display label."""
        version = self.version_var.get()
        pack_format = get_pack_format(version)
        
        if pack_format:
            self.format_label.config(text=f"(pack_format: {pack_format})")
        else:
            self.format_label.config(text="(알 수 없는 버전)")
    
    def get_version(self) -> str:
        """
        Get selected Minecraft version.
        
        Returns:
            Version string (e.g., "1.21.4")
        """
        return self.version_var.get()
    
    def set_version(self, version: str) -> None:
        """
        Set the selected version.
        
        Args:
            version: Version string to select
        """
        self.version_var.set(version)
        self._update_pack_format()
