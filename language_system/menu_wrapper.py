#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menu Wrapper for Language Support
Non-intrusive wrapper that extends the main menu with language selection
"""

import logging
from typing import Callable
from functools import wraps

# Import telegram modules if available (optional for testing)
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import CallbackContext
    TELEGRAM_AVAILABLE = True
except ImportError:
    Update = object
    InlineKeyboardButton = object
    InlineKeyboardMarkup = object
    CallbackContext = object
    TELEGRAM_AVAILABLE = False

# Import middleware - try relative import first, then absolute
try:
    from .language_middleware import get_middleware
except ImportError:
    from language_middleware import get_middleware

logger = logging.getLogger(__name__)


def wrap_main_menu(original_main_menu: Callable) -> Callable:
    """
    Wrap the original show_main_menu function to add language support.
    
    This wrapper:
    1. Calls the original show_main_menu function
    2. Intercepts before the message is sent
    3. Adds language selection button
    4. Translates menu items if possible
    
    Note: The actual method in tdata.py is show_main_menu(update, user_id)
    
    Args:
        original_main_menu: Original show_main_menu method
        
    Returns:
        Wrapped show_main_menu function
    """
    @wraps(original_main_menu)
    def wrapped_main_menu(self, update: Update, user_id: int):
        """
        Wrapped version of show_main_menu that adds language support.
        
        Note: The signature matches the actual show_main_menu(update, user_id) in tdata.py
        """
        # Verify user_id is valid
        if user_id is None:
            # Try to get from update if not provided
            if update.effective_user:
                user_id = update.effective_user.id
            elif update.callback_query and update.callback_query.from_user:
                user_id = update.callback_query.from_user.id
            else:
                # Fall back to original if we can't get user ID
                return original_main_menu(self, update, user_id)
        
        # Get middleware
        middleware = get_middleware()
        user_lang = middleware.get_user_language(user_id)
        
        # Store original method temporarily
        original_edit_method = None
        
        if update.callback_query:
            query = update.callback_query
            original_edit_method = query.edit_message_text
            
            # Create a wrapper for edit_message_text
            def wrapped_edit(*args, **kwargs):
                # Check if we have keyboard in kwargs
                if 'reply_markup' in kwargs:
                    keyboard = kwargs['reply_markup']
                    if isinstance(keyboard, InlineKeyboardMarkup):
                        # Add language button to keyboard
                        buttons = list(keyboard.inline_keyboard)
                        
                        # Insert language button before the last button
                        lang_button_text = middleware.translate_for_user(
                            user_id,
                            "menu.select_language"
                        )
                        
                        insert_position = len(buttons) - 1 if buttons else 0
                        buttons.insert(insert_position, [
                            InlineKeyboardButton(
                                lang_button_text,
                                callback_data="lang_select"
                            )
                        ])
                        
                        # Create new keyboard with language button
                        kwargs['reply_markup'] = InlineKeyboardMarkup(buttons)
                
                # Call original method
                return original_edit_method(*args, **kwargs)
            
            # Temporarily replace the method
            query.edit_message_text = wrapped_edit
        
        try:
            # Call original show_main_menu with correct signature
            result = original_main_menu(self, update, user_id)
            return result
        finally:
            # Restore original methods
            if original_edit_method and update.callback_query:
                update.callback_query.edit_message_text = original_edit_method
    
    return wrapped_main_menu


def apply_menu_wrapper(bot_instance):
    """
    Apply the menu wrapper to a bot instance.
    
    This function patches the bot's show_main_menu method with our wrapper.
    Note: The actual method in tdata.py is 'show_main_menu', not 'main_menu'.
    
    Args:
        bot_instance: EnhancedBot instance to patch
    """
    if hasattr(bot_instance, 'show_main_menu'):
        original_method = bot_instance.show_main_menu
        wrapped_method = wrap_main_menu(original_method)
        
        # Replace the method using descriptor protocol
        # We use __get__ instead of types.MethodType to properly bind the method
        # without causing double-binding issues. The wrapped_method already has
        # 'self' as a parameter, so __get__ correctly binds it to the instance.
        bot_instance.show_main_menu = wrapped_method.__get__(bot_instance, type(bot_instance))
        
        logger.info("✅ Main menu (show_main_menu) wrapped with language support")
    else:
        logger.warning("⚠️ Bot instance does not have show_main_menu method")
