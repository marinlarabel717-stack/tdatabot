#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Manager for TDataBot
Manages translations using JSON files with automatic fallback
"""

import json
import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class LanguageManager:
    """
    Manages translations for the bot with automatic fallback mechanism.
    
    Features:
    - JSON-based translation files
    - Automatic fallback to default language
    - Nested key support (e.g., 'menu.start')
    - Runtime language switching
    """
    
    def __init__(self, lang_dir: str = "lang", default_lang: str = "en"):
        """
        Initialize the language manager.
        
        Args:
            lang_dir: Directory containing language JSON files
            default_lang: Default language code (fallback)
        """
        self.lang_dir = Path(lang_dir)
        self.default_lang = default_lang
        self.languages: Dict[str, Dict[str, Any]] = {}
        self.supported_languages = []
        
        # Load all available languages
        self._load_languages()
        
    def _load_languages(self):
        """Load all language files from the lang directory."""
        if not self.lang_dir.exists():
            logger.warning(f"Language directory not found: {self.lang_dir}")
            self.lang_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Find all JSON files in the lang directory
        for lang_file in self.lang_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
                    self.supported_languages.append(lang_code)
                    logger.info(f"✅ Loaded language: {lang_code}")
            except Exception as e:
                logger.error(f"❌ Failed to load language file {lang_file}: {e}")
        
        if not self.languages:
            logger.warning("⚠️ No language files loaded, creating default English")
            self._create_default_language()
    
    def _create_default_language(self):
        """Create a default English language file if none exist."""
        default_translations = {
            "menu": {
                "welcome": "Welcome to TDataBot",
                "select_language": "🌐 Select Language"
            },
            "language": {
                "changed": "✅ Language changed to English",
                "current": "Current language: English"
            }
        }
        
        en_path = self.lang_dir / "en.json"
        try:
            with open(en_path, 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, indent=2, ensure_ascii=False)
            self.languages['en'] = default_translations
            self.supported_languages.append('en')
            logger.info(f"✅ Created default language file: {en_path}")
        except Exception as e:
            logger.error(f"❌ Failed to create default language file: {e}")
    
    def get(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Get a translation by key with automatic fallback.
        
        Args:
            key: Translation key (supports dot notation, e.g., 'menu.welcome')
            lang: Language code (uses default if None)
            **kwargs: Format variables for the translation string
            
        Returns:
            Translated string with fallback to default language or key itself
        """
        if lang is None:
            lang = self.default_lang
        
        # Try to get translation in requested language
        translation = self._get_nested(self.languages.get(lang, {}), key)
        
        # Fallback to default language if not found
        if translation is None and lang != self.default_lang:
            translation = self._get_nested(
                self.languages.get(self.default_lang, {}), 
                key
            )
        
        # Final fallback to key itself
        if translation is None:
            logger.warning(f"Translation not found: {key} (lang: {lang})")
            translation = key
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Translation formatting error for '{key}': {e}")
        
        return translation
    
    def _get_nested(self, data: Dict, key: str) -> Optional[str]:
        """
        Get a nested value from dictionary using dot notation.
        
        Args:
            data: Dictionary to search
            key: Dot-separated key (e.g., 'menu.welcome')
            
        Returns:
            Value if found, None otherwise
        """
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get the native name of a language.
        
        Args:
            lang_code: Language code
            
        Returns:
            Native language name
        """
        names = {
            'en': 'English',
            'zh': '中文',
            'ru': 'Русский',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'ja': '日本語',
            'ko': '한국어',
        }
        return names.get(lang_code, lang_code.upper())
    
    def reload(self):
        """Reload all language files."""
        self.languages.clear()
        self.supported_languages.clear()
        self._load_languages()
        logger.info("🔄 Languages reloaded")


# Global language manager instance
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """
    Get the global language manager instance.
    
    Returns:
        Global LanguageManager instance
    """
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def translate(key: str, lang: str = None, **kwargs) -> str:
    """
    Convenience function for translation.
    
    Args:
        key: Translation key
        lang: Language code
        **kwargs: Format variables
        
    Returns:
        Translated string
    """
    return get_language_manager().get(key, lang, **kwargs)
