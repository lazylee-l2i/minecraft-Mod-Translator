"""Mod list panel for displaying and managing mod files."""
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import List, Optional, Callable

from ..styles import Spacing, Colors, Fonts
from ...config.constants import INPUT_MODS_DIR
from ...core.jar_extractor import extract_mod_info, get_language_file_count
from ...models.mod_info import ModInfo
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ModListPanel(ttk.LabelFrame):
    """
    Panel for displaying and managing mod files.
    
    Shows a list of mods with their info and allows adding/removing mods.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize mod list panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="모드 목록", padding=Spacing.MD)
        
        self._mods: List[ModInfo] = []
        
        self._setup_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _setup_widgets(self) -> None:
        """Create panel widgets."""
        # Button frame
        self.btn_frame = ttk.Frame(self)
        
        self.add_btn = ttk.Button(
            self.btn_frame,
            text="➕ 모드 추가",
            command=self._on_add_mods
        )
        
        self.remove_btn = ttk.Button(
            self.btn_frame,
            text="➖ 선택 제거",
            command=self._on_remove_selected
        )
        
        self.clear_btn = ttk.Button(
            self.btn_frame,
            text="🗑️ 전체 삭제",
            command=self._on_clear_all
        )
        
        self.refresh_btn = ttk.Button(
            self.btn_frame,
            text="🔄 새로고침",
            command=self._on_refresh
        )
        
        # Treeview for mod list
        columns = ("name", "version", "mod_id", "lang_files")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=8
        )
        
        # Column headings
        self.tree.heading("name", text="모드 이름")
        self.tree.heading("version", text="버전")
        self.tree.heading("mod_id", text="Mod ID")
        self.tree.heading("lang_files", text="언어 파일")
        
        # Column widths
        self.tree.column("name", width=200)
        self.tree.column("version", width=100)
        self.tree.column("mod_id", width=150)
        self.tree.column("lang_files", width=80)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Status label
        self.status_label = ttk.Label(
            self,
            text="모드 파일을 추가하거나 input_mods 폴더에 넣어주세요.",
            font=Fonts.SMALL
        )
    
    def _setup_layout(self) -> None:
        """Arrange widgets."""
        # Buttons
        self.btn_frame.pack(fill=tk.X, pady=(0, Spacing.SM))
        self.add_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        self.remove_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        self.clear_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        self.refresh_btn.pack(side=tk.LEFT, padx=Spacing.XS)
        
        # Treeview with scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status
        self.status_label.pack(fill=tk.X, pady=(Spacing.SM, 0))
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.tree.bind("<Delete>", lambda e: self._on_remove_selected())
    
    def _on_add_mods(self) -> None:
        """Handle add mods button click."""
        files = filedialog.askopenfilenames(
            title="모드 파일 선택",
            filetypes=[("JAR 파일", "*.jar"), ("모든 파일", "*.*")],
            initialdir=INPUT_MODS_DIR if INPUT_MODS_DIR.exists() else None
        )
        
        if files:
            added = 0
            for file_path in files:
                path = Path(file_path)
                if self._add_mod(path):
                    added += 1
            
            self._update_status()
            logger.info(f"Added {added} mod(s)")
    
    def _on_remove_selected(self) -> None:
        """Remove selected mods from list."""
        selected = self.tree.selection()
        
        for item_id in selected:
            # Find and remove from internal list
            item = self.tree.item(item_id)
            mod_id = item["values"][2]  # mod_id column
            
            self._mods = [m for m in self._mods if m.mod_id != mod_id]
            self.tree.delete(item_id)
        
        self._update_status()
    
    def _on_clear_all(self) -> None:
        """Clear all mods from list."""
        self._mods.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self._update_status()
    
    def _on_refresh(self) -> None:
        """Refresh mod list from input_mods directory."""
        self._on_clear_all()
        
        if INPUT_MODS_DIR.exists():
            for jar_file in INPUT_MODS_DIR.glob("*.jar"):
                self._add_mod(jar_file)
        
        self._update_status()
    
    def _add_mod(self, jar_path: Path) -> bool:
        """
        Add a mod to the list.
        
        Args:
            jar_path: Path to JAR file
            
        Returns:
            True if added successfully
        """
        # Check if already added
        for mod in self._mods:
            if mod.jar_path == jar_path:
                return False
        
        # Extract mod info
        mod_info = extract_mod_info(jar_path)
        if not mod_info:
            return False
        
        # Count language files
        lang_count = get_language_file_count(jar_path)
        
        # Add to internal list
        self._mods.append(mod_info)
        
        # Add to treeview
        self.tree.insert(
            "",
            tk.END,
            values=(
                mod_info.name,
                mod_info.version,
                mod_info.mod_id,
                lang_count
            )
        )
        
        return True
    
    def _update_status(self) -> None:
        """Update status label."""
        count = len(self._mods)
        
        if count == 0:
            self.status_label.config(
                text="모드 파일을 추가하거나 input_mods 폴더에 넣어주세요."
            )
        else:
            self.status_label.config(
                text=f"총 {count}개의 모드가 준비되었습니다."
            )
    
    def get_mods(self) -> List[ModInfo]:
        """
        Get list of added mods.
        
        Returns:
            List of ModInfo objects
        """
        return self._mods.copy()
    
    def get_mod_count(self) -> int:
        """
        Get number of mods in list.
        
        Returns:
            Number of mods
        """
        return len(self._mods)
