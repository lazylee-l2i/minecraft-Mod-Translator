"""Main application window."""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from pathlib import Path
from typing import Optional, List

from .styles import configure_styles, Colors, Spacing
from .components.llm_config_panel import LLMConfigPanel
from .components.version_selector import VersionSelector
from .components.mod_list_panel import ModListPanel
from .components.progress_panel import ProgressPanel

from ..config.constants import WINDOW_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE, RESULT_PACK_DIR
from ..core.translator import create_translator
from ..core.jar_extractor import extract_language_files, extract_mod_info, has_korean_translation
from ..core.cache_manager import CacheManager
from ..core.resource_pack_builder import build_resource_pack
from ..models.translation_data import TranslationResult, TranslationProgress
from ..utils.logger import setup_logging, get_logger
from ..utils.file_manager import ensure_directories

logger = get_logger(__name__)


class MainWindow:
    """
    Main application window for Minecraft Mod Translator.
    
    Provides UI for configuring translation settings and running
    the translation workflow.
    """
    
    def __init__(self):
        """Initialize main window."""
        # Initialize logging
        setup_logging()
        logger.info("Starting Minecraft Mod Translator v2.0")
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize cache manager
        self.cache_manager = CacheManager()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)
        
        # Configure styles
        configure_styles()
        
        # Translation state
        self._is_translating = False
        self._cancel_requested = False
        
        # Setup UI
        self._setup_ui()
        
        # Load mods from input directory
        self.mod_list.after(100, self.mod_list._on_refresh)
    
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=Spacing.MD)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🎮 Minecraft Mod Translator",
            font=("맑은 고딕", 18, "bold")
        )
        title_label.pack(pady=(0, Spacing.MD))
        
        # LLM Configuration Panel
        self.llm_panel = LLMConfigPanel(main_frame)
        self.llm_panel.pack(fill=tk.X, pady=Spacing.SM)
        
        # Minecraft Version Selector
        self.version_selector = VersionSelector(main_frame)
        self.version_selector.pack(fill=tk.X, pady=Spacing.SM)
        
        # Mod List Panel
        self.mod_list = ModListPanel(main_frame)
        self.mod_list.pack(fill=tk.BOTH, expand=True, pady=Spacing.SM)
        
        # Progress Panel
        self.progress = ProgressPanel(main_frame)
        self.progress.pack(fill=tk.BOTH, expand=True, pady=Spacing.SM)
        
        # Control Buttons
        self._setup_buttons(main_frame)
    
    def _setup_buttons(self, parent: tk.Widget) -> None:
        """Setup control buttons."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=Spacing.MD)
        
        # Translate button
        self.translate_btn = ttk.Button(
            btn_frame,
            text="🚀 번역 시작",
            command=self._on_translate,
            style="Primary.TButton"
        )
        self.translate_btn.pack(side=tk.LEFT, padx=Spacing.SM)
        
        # Cancel button (initially disabled)
        self.cancel_btn = ttk.Button(
            btn_frame,
            text="⏹️ 취소",
            command=self._on_cancel,
            state="disabled"
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=Spacing.SM)
        
        # Open output folder button
        self.open_folder_btn = ttk.Button(
            btn_frame,
            text="📁 결과 폴더 열기",
            command=self._on_open_folder
        )
        self.open_folder_btn.pack(side=tk.RIGHT, padx=Spacing.SM)
        
        # Clear cache button
        self.clear_cache_btn = ttk.Button(
            btn_frame,
            text="🗑️ 캐시 삭제",
            command=self._on_clear_cache
        )
        self.clear_cache_btn.pack(side=tk.RIGHT, padx=Spacing.SM)
    
    def _on_translate(self) -> None:
        """Handle translate button click."""
        # Validate configuration
        error = self.llm_panel.validate()
        if error:
            messagebox.showerror("설정 오류", error)
            return
        
        # Check if mods are loaded
        mods = self.mod_list.get_mods()
        if not mods:
            messagebox.showwarning("모드 없음", "번역할 모드를 추가해주세요.")
            return
        
        # Start translation in background thread
        self._is_translating = True
        self._cancel_requested = False
        
        # Update UI state
        self.translate_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress.reset()
        
        # Run translation in background
        thread = threading.Thread(target=self._run_translation, daemon=True)
        thread.start()
    
    def _run_translation(self) -> None:
        """Run translation workflow in background thread."""
        try:
            llm_config = self.llm_panel.get_config()
            mc_version = self.version_selector.get_version()
            mods = self.mod_list.get_mods()
            
            # Create translator with batch size
            batch_size = llm_config.get("batch_size", 50)
            translator = create_translator(
                provider=llm_config["provider"],
                api_key=llm_config["api_key"],
                model=llm_config["model"],
                server_url=llm_config["server_url"]
            )
            translator.batch_size = batch_size
            
            # Get cache option
            use_cache = llm_config.get("use_cache", True)
            skip_existing = llm_config.get("skip_existing", True)
            
            self._log("info", f"번역 엔진: {llm_config['provider']} ({llm_config['model']})")
            self._log("info", f"배치 크기: {batch_size}항목")
            self._log("info", f"캐시 사용: {'예' if use_cache else '아니오'}")
            self._log("info", f"원본 번역 포함 모드 생략: {'예' if skip_existing else '아니오'}")
            self._log("info", f"마인크래프트 버전: {mc_version}")
            self._log("info", f"총 {len(mods)}개의 모드 처리 예정")
            
            # Process each mod
            translations: List[TranslationResult] = []
            
            for i, mod in enumerate(mods):
                if self._cancel_requested:
                    self._log("warning", "번역이 취소되었습니다.")
                    break
                
                # Update progress
                progress = TranslationProgress(
                    total_mods=len(mods),
                    current_mod_index=i,
                    current_mod_name=mod.display_name,
                    status=f"{mod.name} 처리 중..."
                )
                self._update_progress(progress)
                self._log("info", f"처리 중: {mod.display_name}")
                
                # Skip mods that already have Korean translation in JAR
                if skip_existing:
                    if has_korean_translation(mod.jar_path):
                        self._log("success", f"✓ 원본에 한글 번역 포함: {mod.mod_id} (생략)")
                        continue
                
                # Check cache (only if use_cache is enabled)
                if use_cache:
                    cached = self.cache_manager.get_cached_translation(mod.mod_id, mod.version)
                    
                    if cached:
                        self._log("success", f"캐시에서 로드: {mod.mod_id}")
                        translations.append(TranslationResult(
                            mod_id=mod.mod_id,
                            mod_version=mod.version,
                            original_content={},
                            translated_content=cached,
                            from_cache=True
                        ))
                        continue
                
                # Extract and translate language files
                for lang_file in extract_language_files(mod.jar_path):
                    if self._cancel_requested:
                        break
                    
                    self._log("info", f"번역 중: {lang_file.mod_id} ({len(lang_file.content)}항목)")
                    
                    try:
                        # Use batched translation for large files
                        translated = translator.translate_batched(
                            lang_file.content,
                            progress_callback=lambda cur, tot: self._log(
                                "info", f"  배치 {cur}/{tot} 처리 중..."
                            )
                        )
                        
                        # Save to cache
                        self.cache_manager.save_translation(
                            mod.mod_id,
                            mod.version,
                            translated
                        )
                        
                        translations.append(TranslationResult(
                            mod_id=lang_file.mod_id,
                            mod_version=mod.version,
                            original_content=lang_file.content,
                            translated_content=translated,
                            from_cache=False
                        ))
                        
                        self._log("success", f"번역 완료: {lang_file.mod_id}")
                        
                    except Exception as e:
                        self._log("error", f"번역 실패 ({lang_file.mod_id}): {e}")
            
            if self._cancel_requested:
                self._set_complete(False, "번역이 취소되었습니다.")
                return
            
            if not translations:
                self._set_complete(False, "번역된 모드가 없습니다.")
                return
            
            # Build resource pack
            self._log("info", "리소스팩 생성 중...")
            
            progress = TranslationProgress(
                total_mods=len(mods),
                current_mod_index=len(mods),
                current_mod_name="",
                status="리소스팩 생성 중..."
            )
            self._update_progress(progress)
            
            output_path = build_resource_pack(translations, mc_version)
            
            self._log("success", f"리소스팩 생성 완료: {output_path.name}")
            self._set_complete(True, f"result_pack/{output_path.name} 생성 완료!")
            
        except Exception as e:
            logger.exception("Translation failed")
            self._log("error", f"오류 발생: {e}")
            self._set_complete(False, str(e))
        
        finally:
            self._is_translating = False
            self.root.after(0, lambda: self.translate_btn.config(state="normal"))
            self.root.after(0, lambda: self.cancel_btn.config(state="disabled"))
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self._is_translating:
            self._cancel_requested = True
            self.cancel_btn.config(state="disabled")
            self.progress.add_log("취소 요청됨...", "warning")
    
    def _on_open_folder(self) -> None:
        """Open result folder in file explorer."""
        import os
        import subprocess
        
        RESULT_PACK_DIR.mkdir(exist_ok=True)
        
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', str(RESULT_PACK_DIR)])
        else:  # macOS, Linux
            subprocess.run(['open' if os.name == 'darwin' else 'xdg-open', str(RESULT_PACK_DIR)])
    
    def _on_clear_cache(self) -> None:
        """Clear translation cache."""
        result = messagebox.askyesno(
            "캐시 삭제",
            "모든 번역 캐시를 삭제하시겠습니까?\n이 작업은 취소할 수 없습니다."
        )
        
        if result:
            count = self.cache_manager.clear_cache()
            messagebox.showinfo("완료", f"{count}개의 캐시가 삭제되었습니다.")
            self.progress.add_log(f"캐시 삭제: {count}개", "info")
    
    def _update_progress(self, progress: TranslationProgress) -> None:
        """Update progress panel from background thread."""
        self.root.after(0, lambda: self.progress.update_progress(progress))
    
    def _log(self, level: str, message: str) -> None:
        """Add log message from background thread."""
        self.root.after(0, lambda: self.progress.add_log(message, level))
        
        # Also log to file
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _set_complete(self, success: bool, message: str) -> None:
        """Set completion state from background thread."""
        self.root.after(0, lambda: self.progress.set_complete(success, message))
    
    def run(self) -> None:
        """Start the application."""
        logger.info("Application started")
        self.root.mainloop()
        logger.info("Application closed")
