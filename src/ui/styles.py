"""UI style definitions and constants."""
import tkinter as tk
from tkinter import ttk


# Color Palette
class Colors:
    """Application color palette."""
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    SECONDARY = "#4CAF50"
    BACKGROUND = "#F5F5F5"
    SURFACE = "#FFFFFF"
    TEXT = "#212121"
    TEXT_SECONDARY = "#757575"
    ERROR = "#F44336"
    WARNING = "#FF9800"
    SUCCESS = "#4CAF50"
    BORDER = "#E0E0E0"


# Font configurations
class Fonts:
    """Application font configurations."""
    TITLE = ("맑은 고딕", 14, "bold")
    HEADING = ("맑은 고딕", 12, "bold")
    BODY = ("맑은 고딕", 10)
    SMALL = ("맑은 고딕", 9)
    MONO = ("Consolas", 10)


# Padding and margin values
class Spacing:
    """Spacing constants."""
    XS = 2
    SM = 5
    MD = 10
    LG = 15
    XL = 20


def configure_styles() -> None:
    """Configure ttk styles for the application."""
    style = ttk.Style()
    
    # Use clam theme as base (works well on Windows)
    style.theme_use("clam")
    
    # Configure TFrame
    style.configure(
        "TFrame",
        background=Colors.BACKGROUND
    )
    
    # Configure card-like frames
    style.configure(
        "Card.TFrame",
        background=Colors.SURFACE,
        relief="solid",
        borderwidth=1
    )
    
    # Configure TLabelframe
    style.configure(
        "TLabelframe",
        background=Colors.SURFACE,
        foreground=Colors.TEXT
    )
    style.configure(
        "TLabelframe.Label",
        font=Fonts.HEADING,
        foreground=Colors.TEXT
    )
    
    # Configure TLabel
    style.configure(
        "TLabel",
        background=Colors.SURFACE,
        foreground=Colors.TEXT,
        font=Fonts.BODY
    )
    
    # Status labels
    style.configure(
        "Success.TLabel",
        foreground=Colors.SUCCESS
    )
    style.configure(
        "Error.TLabel",
        foreground=Colors.ERROR
    )
    style.configure(
        "Warning.TLabel",
        foreground=Colors.WARNING
    )
    
    # Configure TButton
    style.configure(
        "TButton",
        font=Fonts.BODY,
        padding=(Spacing.MD, Spacing.SM)
    )
    
    # Primary button
    style.configure(
        "Primary.TButton",
        background=Colors.PRIMARY,
        foreground="white"
    )
    style.map(
        "Primary.TButton",
        background=[("active", Colors.PRIMARY_DARK)]
    )
    
    # Configure TEntry
    style.configure(
        "TEntry",
        font=Fonts.BODY,
        padding=Spacing.SM
    )
    
    # Configure TCombobox
    style.configure(
        "TCombobox",
        font=Fonts.BODY,
        padding=Spacing.SM
    )
    
    # Configure Treeview
    style.configure(
        "Treeview",
        font=Fonts.BODY,
        rowheight=25
    )
    style.configure(
        "Treeview.Heading",
        font=Fonts.HEADING
    )
    
    # Configure TProgressbar
    style.configure(
        "TProgressbar",
        thickness=20,
        troughcolor=Colors.BORDER,
        background=Colors.PRIMARY
    )
