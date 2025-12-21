#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Middleware for TDataBot
Provides global language context and dynamic translation injection
"""

import logging
import sqlite3
from typing import Callable, Optional, Any
from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext

from language_manager import get_language_manager

logger = logging.getLogger(__name__)


class LanguageMiddleware:
    """
    Middleware for managing user language preferences.
    
    Features:
    - Store and retrieve user language preferences
    - Provide language context for translations
    - Integration with database
    """
    
    def __init__(self, db_path: str = "bot_data.db"):
        """
        Initialize the language middleware.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._ensure_language_table()
        self.lang_manager = get_language_manager()
    
    def _ensure_language_table(self):
        """Ensure the language preferences table exists."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_language (
                    user_id INTEGER PRIMARY KEY,
                    language_code TEXT NOT NULL DEFAULT 'en',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Language table initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize language table: {e}")
    
    def get_user_language(self, user_id: int) -> str:
        """
        Get the user's preferred language.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Language code (defaults to 'en')
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT language_code FROM user_language WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                return 'en'  # Default to English
        except Exception as e:
            logger.error(f"❌ Failed to get user language: {e}")
            return 'en'
    
    def set_user_language(self, user_id: int, language_code: str) -> bool:
        """
        Set the user's preferred language.
        
        Args:
            user_id: Telegram user ID
            language_code: Language code to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use INSERT OR REPLACE to handle both new and existing users
            cursor.execute("""
                INSERT OR REPLACE INTO user_language (user_id, language_code, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, language_code))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Set language for user {user_id}: {language_code}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set user language: {e}")
            return False
    
    def translate_for_user(self, user_id: int, key: str, **kwargs) -> str:
        """
        Translate a key for a specific user.
        
        Args:
            user_id: Telegram user ID
            key: Translation key
            **kwargs: Format variables
            
        Returns:
            Translated string
        """
        lang = self.get_user_language(user_id)
        return self.lang_manager.get(key, lang, **kwargs)


# Global middleware instance
_middleware: Optional[LanguageMiddleware] = None


def get_middleware() -> LanguageMiddleware:
    """
    Get the global language middleware instance.
    
    Returns:
        Global LanguageMiddleware instance
    """
    global _middleware
    if _middleware is None:
        _middleware = LanguageMiddleware()
    return _middleware


def with_language(func: Callable) -> Callable:
    """
    Decorator to inject language context into handler functions.
    
    Usage:
        @with_language
        def my_handler(update, context, lang_manager):
            text = lang_manager.get('some.key')
            ...
    
    Args:
        func: Handler function to wrap
        
    Returns:
        Wrapped function with language context
    """
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        # Get user ID
        user_id = None
        if update.effective_user:
            user_id = update.effective_user.id
        elif update.callback_query and update.callback_query.from_user:
            user_id = update.callback_query.from_user.id
        
        if user_id is None:
            logger.warning("Could not determine user ID for language context")
            return func(update, context, *args, **kwargs)
        
        # Get user's language
        middleware = get_middleware()
        user_lang = middleware.get_user_language(user_id)
        
        # Create a simple translation function for this user
        def t(key: str, **format_kwargs) -> str:
            return middleware.translate_for_user(user_id, key, **format_kwargs)
        
        # Inject translation function into context
        if not hasattr(context, 'user_data'):
            context.user_data = {}
        context.user_data['translate'] = t
        context.user_data['user_lang'] = user_lang
        
        return func(update, context, *args, **kwargs)
    
    return wrapper


def translate_menu_text(menu_func: Callable) -> Callable:
    """
    Decorator to automatically translate menu text based on user language.
    
    This decorator intercepts menu creation and translates button texts.
    
    Args:
        menu_func: Menu creation function
        
    Returns:
        Wrapped function with automatic translation
    """
    @wraps(menu_func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = menu_func(*args, **kwargs)
        
        # If result contains Update object, we can translate
        # This is a placeholder for future enhancement
        # For now, we'll rely on the integration module to handle this
        
        return result
    
    return wrapper
