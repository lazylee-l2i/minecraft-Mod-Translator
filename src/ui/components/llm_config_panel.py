"""LLM configuration panel with provider selection, model dropdown, and API key input."""
import tkinter as tk
from tkinter import ttk
import threading
from typing import Dict, Any, Optional, List

from ..styles import Colors, Fonts, Spacing
from ...core.translator import LLMProvider
from ...core.model_fetcher import (
    fetch_ollama_models,
    fetch_openai_models,
    fetch_openrouter_models,
    get_default_models
)


class LLMConfigPanel(ttk.LabelFrame):
    """
    Panel for LLM provider selection and API key input.
    
    Features:
    - Provider selection dropdown
    - Model selection with auto-fetch capability
    - API keys are stored in memory only and never saved to disk
    - Batch size configuration for large translation optimization
    """
    
    # Default models for each provider
    DEFAULT_MODELS = {
        LLMProvider.OPENAI: "gpt-4o",
        LLMProvider.OPENROUTER: "openai/gpt-4o",
        LLMProvider.OLLAMA: "llama3.2",
    }
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize LLM config panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="번역 엔진 설정", padding=Spacing.MD)
        
        self._cached_models: Dict[str, List[str]] = {}
        self._is_fetching = False
        
        self._setup_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Initialize model list with defaults
        self._update_model_list()
    
    def _setup_widgets(self) -> None:
        """Create panel widgets."""
        # Provider Selection
        self.provider_label = ttk.Label(self, text="번역 엔진:")
        self.provider_var = tk.StringVar(value=LLMProvider.OPENAI)
        self.provider_combo = ttk.Combobox(
            self,
            textvariable=self.provider_var,
            values=LLMProvider.all(),
            state="readonly",
            width=18
        )
        
        # API Key Input (1회성, 메모리에만 저장)
        self.api_key_label = ttk.Label(self, text="API Key:")
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(
            self, 
            textvariable=self.api_key_var, 
            show="•",  # 마스킹
            width=40
        )
        
        # Show/Hide API Key button
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_btn = ttk.Checkbutton(
            self,
            text="표시",
            variable=self.show_key_var,
            command=self._toggle_key_visibility
        )
        
        # Model Selection (Combobox instead of Entry)
        self.model_label = ttk.Label(self, text="모델:")
        self.model_var = tk.StringVar(value=self.DEFAULT_MODELS[LLMProvider.OPENAI])
        self.model_combo = ttk.Combobox(
            self,
            textvariable=self.model_var,
            values=get_default_models(LLMProvider.OPENAI),
            width=30
        )
        
        # Refresh models button
        self.refresh_btn = ttk.Button(
            self,
            text="🔄 모델 목록",
            command=self._on_refresh_models,
            width=12
        )
        
        # Model status label
        self.model_status_label = ttk.Label(
            self,
            text="",
            font=Fonts.SMALL,
            foreground=Colors.TEXT_SECONDARY
        )
        
        # Ollama Server URL
        self.server_label = ttk.Label(self, text="서버 URL:")
        self.server_url_var = tk.StringVar(value="http://localhost:11434")
        self.server_url_entry = ttk.Entry(
            self, 
            textvariable=self.server_url_var, 
            width=25,
            state="disabled"
        )
        
        # Batch size setting (for large JSON optimization)
        self.batch_label = ttk.Label(self, text="배치 크기:")
        self.batch_size_var = tk.IntVar(value=50)
        self.batch_spinbox = ttk.Spinbox(
            self,
            from_=10,
            to=200,
            increment=10,
            textvariable=self.batch_size_var,
            width=8
        )
        self.batch_info_label = ttk.Label(
            self,
            text="(항목/배치)",
            font=Fonts.SMALL,
            foreground=Colors.TEXT_SECONDARY
        )
        
        # Use cache option (skip already translated mods)
        self.use_cache_var = tk.BooleanVar(value=True)  # 기본값: 캐시 사용
        self.use_cache_check = ttk.Checkbutton(
            self,
            text="번역 캐시 사용 (이전 번역 결과 재사용)",
            variable=self.use_cache_var
        )
        
        # Skip mods with existing Korean translation in JAR
        self.skip_existing_var = tk.BooleanVar(value=True)  # 기본값: 원본에 번역 있으면 생략
        self.skip_existing_check = ttk.Checkbutton(
            self,
            text="원본에 한글 번역 포함된 모드 생략",
            variable=self.skip_existing_var
        )
        
        # Info label
        self.info_label = ttk.Label(
            self,
            text="💡 API 키 입력 후 '모델 목록' 버튼으로 사용 가능한 모델을 불러오세요.",
            font=Fonts.SMALL,
            foreground=Colors.TEXT_SECONDARY
        )
    
    def _setup_layout(self) -> None:
        """Arrange widgets in grid layout."""
        # Row 0: Provider and API Key
        self.provider_label.grid(row=0, column=0, sticky="e", padx=Spacing.SM, pady=Spacing.SM)
        self.provider_combo.grid(row=0, column=1, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        self.api_key_label.grid(row=0, column=2, sticky="e", padx=Spacing.SM, pady=Spacing.SM)
        self.api_key_entry.grid(row=0, column=3, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        self.show_key_btn.grid(row=0, column=4, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # Row 1: Model selection with refresh button
        self.model_label.grid(row=1, column=0, sticky="e", padx=Spacing.SM, pady=Spacing.SM)
        self.model_combo.grid(row=1, column=1, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        self.refresh_btn.grid(row=1, column=2, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        self.model_status_label.grid(row=1, column=3, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # Row 2: Server URL and Batch size
        self.server_label.grid(row=2, column=0, sticky="e", padx=Spacing.SM, pady=Spacing.SM)
        self.server_url_entry.grid(row=2, column=1, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        self.batch_label.grid(row=2, column=2, sticky="e", padx=Spacing.SM, pady=Spacing.SM)
        self.batch_spinbox.grid(row=2, column=3, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        self.batch_info_label.grid(row=2, column=4, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # Row 3: Cache option and skip existing
        self.use_cache_check.grid(row=3, column=0, columnspan=2, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        self.skip_existing_check.grid(row=3, column=2, columnspan=3, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
        
        # Row 4: Info
        self.info_label.grid(row=4, column=0, columnspan=5, sticky="w", padx=Spacing.SM, pady=Spacing.SM)
    
    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
    
    def _on_provider_change(self, event=None) -> None:
        """Handle provider selection change."""
        provider = self.provider_var.get()
        
        if provider == LLMProvider.OLLAMA:
            # Ollama: API key disabled, server URL enabled
            self.api_key_entry.config(state="disabled")
            self.api_key_var.set("")
            self.server_url_entry.config(state="normal")
            # Auto-fetch Ollama models
            self._on_refresh_models()
        else:
            # Cloud providers: API key enabled, server URL disabled
            self.api_key_entry.config(state="normal")
            self.server_url_entry.config(state="disabled")
        
        # Update model list and default
        self._update_model_list()
        self.model_var.set(self.DEFAULT_MODELS.get(provider, ""))
    
    def _update_model_list(self) -> None:
        """Update model dropdown with cached or default models."""
        provider = self.provider_var.get()
        
        if provider in self._cached_models:
            models = self._cached_models[provider]
        else:
            models = get_default_models(provider)
        
        self.model_combo['values'] = models
        
        if models:
            self.model_status_label.config(text=f"({len(models)}개)")
        else:
            self.model_status_label.config(text="")
    
    def _on_refresh_models(self) -> None:
        """Fetch available models from the provider."""
        if self._is_fetching:
            return
        
        provider = self.provider_var.get()
        api_key = self.api_key_var.get().strip()
        server_url = self.server_url_var.get().strip()
        
        # Check requirements
        if provider != LLMProvider.OLLAMA and not api_key:
            self.model_status_label.config(
                text="API 키를 먼저 입력하세요",
                foreground=Colors.WARNING
            )
            return
        
        self._is_fetching = True
        self.refresh_btn.config(state="disabled")
        self.model_status_label.config(text="로딩 중...", foreground=Colors.TEXT_SECONDARY)
        
        # Fetch in background thread
        thread = threading.Thread(
            target=self._fetch_models_thread,
            args=(provider, api_key, server_url),
            daemon=True
        )
        thread.start()
    
    def _fetch_models_thread(self, provider: str, api_key: str, server_url: str) -> None:
        """Background thread to fetch models."""
        models: List[str] = []
        
        try:
            if provider == LLMProvider.OLLAMA:
                models = fetch_ollama_models(server_url)
            elif provider == LLMProvider.OPENAI:
                models = fetch_openai_models(api_key)
            elif provider == LLMProvider.OPENROUTER:
                models = fetch_openrouter_models(api_key)
        except Exception as e:
            self.after(0, lambda: self._on_fetch_error(str(e)))
            return
        
        self.after(0, lambda: self._on_fetch_complete(provider, models))
    
    def _on_fetch_complete(self, provider: str, models: List[str]) -> None:
        """Handle fetch completion on main thread."""
        self._is_fetching = False
        self.refresh_btn.config(state="normal")
        
        if models:
            self._cached_models[provider] = models
            self.model_combo['values'] = models
            
            # Select first model if current is not in list
            current = self.model_var.get()
            if current not in models:
                self.model_var.set(models[0])
            
            self.model_status_label.config(
                text=f"✅ {len(models)}개 모델",
                foreground=Colors.SUCCESS
            )
        else:
            # Use defaults as fallback
            defaults = get_default_models(provider)
            self.model_combo['values'] = defaults
            self.model_status_label.config(
                text="⚠️ 기본 모델 사용",
                foreground=Colors.WARNING
            )
    
    def _on_fetch_error(self, error: str) -> None:
        """Handle fetch error on main thread."""
        self._is_fetching = False
        self.refresh_btn.config(state="normal")
        self.model_status_label.config(
            text=f"❌ 오류",
            foreground=Colors.ERROR
        )
    
    def _toggle_key_visibility(self) -> None:
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="•")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current LLM configuration.
        
        Returns:
            Dictionary with provider, api_key, model, server_url, batch_size
        """
        return {
            "provider": self.provider_var.get(),
            "api_key": self.api_key_var.get(),  # 메모리에만 존재
            "model": self.model_var.get(),
            "server_url": self.server_url_var.get(),
            "batch_size": self.batch_size_var.get(),
            "use_cache": self.use_cache_var.get(),
            "skip_existing": self.skip_existing_var.get(),
        }
    
    def validate(self) -> Optional[str]:
        """
        Validate configuration.
        
        Returns:
            Error message if validation fails, None if valid
        """
        provider = self.provider_var.get()
        
        if not provider:
            return "번역 엔진을 선택해주세요."
        
        if provider != LLMProvider.OLLAMA:
            api_key = self.api_key_var.get().strip()
            if not api_key:
                return "API 키를 입력해주세요."
        
        model = self.model_var.get().strip()
        if not model:
            return "모델을 선택해주세요."
        
        return None
