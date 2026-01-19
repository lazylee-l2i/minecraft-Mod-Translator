"""Progress panel for displaying translation progress."""
import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..styles import Spacing, Colors, Fonts
from ...models.translation_data import TranslationProgress


class ProgressPanel(ttk.LabelFrame):
    """
    Panel for displaying translation progress.
    
    Shows current mod being processed, progress bar, and status messages.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize progress panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="진행 상황", padding=Spacing.MD)
        
        self._setup_widgets()
        self._setup_layout()
    
    def _setup_widgets(self) -> None:
        """Create panel widgets."""
        # Current mod label
        self.current_mod_label = ttk.Label(
            self,
            text="대기 중...",
            font=Fonts.BODY
        )
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        
        # Progress text
        self.progress_text = ttk.Label(
            self,
            text="0%",
            font=Fonts.SMALL
        )
        
        # Status label
        self.status_label = ttk.Label(
            self,
            text="",
            font=Fonts.SMALL,
            foreground=Colors.TEXT_SECONDARY
        )
        
        # Log text area
        self.log_frame = ttk.Frame(self)
        
        self.log_text = tk.Text(
            self.log_frame,
            height=5,
            width=80,
            font=Fonts.MONO,
            state="disabled",
            wrap=tk.WORD
        )
        
        self.log_scrollbar = ttk.Scrollbar(
            self.log_frame,
            orient=tk.VERTICAL,
            command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)
    
    def _setup_layout(self) -> None:
        """Arrange widgets."""
        # Current mod
        self.current_mod_label.pack(fill=tk.X, pady=(0, Spacing.SM))
        
        # Progress bar with percentage
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=Spacing.SM)
        
        self.progress_bar.pack(in_=progress_frame, side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_text.pack(in_=progress_frame, side=tk.RIGHT, padx=Spacing.SM)
        
        # Status
        self.status_label.pack(fill=tk.X, pady=Spacing.SM)
        
        # Log area
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=Spacing.SM)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_progress(self, progress: TranslationProgress) -> None:
        """
        Update progress display.
        
        Args:
            progress: TranslationProgress object with current state
        """
        # Update current mod label
        if progress.current_mod_name:
            self.current_mod_label.config(
                text=f"처리 중: {progress.current_mod_name} ({progress.current_mod_index + 1}/{progress.total_mods})"
            )
        else:
            self.current_mod_label.config(text="대기 중...")
        
        # Update progress bar
        self.progress_var.set(progress.progress_percent)
        self.progress_text.config(text=f"{progress.progress_percent:.0f}%")
        
        # Update status
        self.status_label.config(text=progress.status)
        
        # Update status color based on state
        if progress.error:
            self.status_label.config(foreground=Colors.ERROR)
        elif progress.is_complete:
            self.status_label.config(foreground=Colors.SUCCESS)
        else:
            self.status_label.config(foreground=Colors.TEXT_SECONDARY)
    
    def add_log(self, message: str, level: str = "info") -> None:
        """
        Add a log message to the log area.
        
        Args:
            message: Log message
            level: Log level (info, warning, error, success)
        """
        self.log_text.config(state="normal")
        
        # Add prefix based on level
        prefix = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }.get(level, "•")
        
        self.log_text.insert(tk.END, f"{prefix} {message}\n")
        self.log_text.see(tk.END)  # Scroll to bottom
        
        self.log_text.config(state="disabled")
    
    def clear_log(self) -> None:
        """Clear the log area."""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def reset(self) -> None:
        """Reset progress panel to initial state."""
        self.current_mod_label.config(text="대기 중...")
        self.progress_var.set(0)
        self.progress_text.config(text="0%")
        self.status_label.config(text="", foreground=Colors.TEXT_SECONDARY)
        self.clear_log()
    
    def set_complete(self, success: bool = True, message: str = "") -> None:
        """
        Set completion state.
        
        Args:
            success: Whether translation completed successfully
            message: Completion message
        """
        self.progress_var.set(100)
        self.progress_text.config(text="100%")
        
        if success:
            self.current_mod_label.config(text="번역 완료! 🎉")
            self.status_label.config(
                text=message or "리소스팩이 성공적으로 생성되었습니다.",
                foreground=Colors.SUCCESS
            )
            self.add_log(message or "번역이 완료되었습니다!", "success")
        else:
            self.current_mod_label.config(text="번역 실패 ❌")
            self.status_label.config(
                text=message or "번역 중 오류가 발생했습니다.",
                foreground=Colors.ERROR
            )
            self.add_log(message or "오류가 발생했습니다.", "error")
