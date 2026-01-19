"""
Minecraft Mod Translator v2.0

ChatGPT 기반 마인크래프트 모드 자동 번역기

Usage:
    python -m src.main

Features:
    - 다중 LLM 지원 (OpenAI GPT, OpenRouter, Ollama)
    - 번역 캐시로 재활용
    - Tkinter GUI
    - Resource Pack 생성
"""
from src.ui.main_window import MainWindow


def main() -> None:
    """Run the Minecraft Mod Translator application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
