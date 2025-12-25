#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Menu Wrapper for Language Support
This module provides a non-intrusive wrapper that properly handles both
callback queries and fresh menu displays.
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
    Enhanced wrapper for show_main_menu that adds language support.
    
    This wrapper:
    1. Calls the original show_main_menu function
    2. Intercepts keyboard creation for both callback queries and new messages
    3. Adds translated language selection button dynamically
    4. Handles all edge cases
    
    Args:
        original_main_menu: Original show_main_menu method
        
    Returns:
        Wrapped show_main_menu function
    """
    @wraps(original_main_menu)
    def wrapped_main_menu(self, update: Update, user_id: int):
        """
        Wrapped version of show_main_menu that adds language support.
        
        This version properly handles both callback queries and fresh messages.
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
                return original_main_menu(update, user_id)
        
        # Get middleware
        middleware = get_middleware()
        
        # Store original methods
        original_edit_method = None
        original_reply_method = None
        
        # Helper function to add language button to keyboard
        def add_language_button(keyboard):
            """Add language button to an existing keyboard markup."""
            if not isinstance(keyboard, InlineKeyboardMarkup):
                return keyboard
            
            # Get translated button text
            lang_button_text = middleware.translate_for_user(
                user_id,
                "menu.select_language"
            )
            
            # Copy existing buttons
            buttons = list(keyboard.inline_keyboard)
            
            # Check if language button already exists to avoid duplication
            has_lang_button = any(
                any(btn.callback_data == "lang_select" for btn in row)
                for row in buttons
            )
            
            if not has_lang_button:
                # Insert language button before the last button (typically "Status")
                insert_position = len(buttons) - 1 if buttons else 0
                buttons.insert(insert_position, [
                    InlineKeyboardButton(
                        lang_button_text,
                        callback_data="lang_select"
                    )
                ])
            
            return InlineKeyboardMarkup(buttons)
        
        # Wrap callback query edit_message_text if available
        if update.callback_query:
            query = update.callback_query
            original_edit_method = query.edit_message_text
            
            def wrapped_edit(*args, **kwargs):
                """Wrapper for edit_message_text to add language button."""
                if 'reply_markup' in kwargs:
                    kwargs['reply_markup'] = add_language_button(kwargs['reply_markup'])
                return original_edit_method(*args, **kwargs)
            
            query.edit_message_text = wrapped_edit
        
        # Wrap message reply_text for fresh messages
        if hasattr(update, 'message') and update.message:
            original_reply_method = update.message.reply_text
            
            def wrapped_reply(*args, **kwargs):
                """Wrapper for reply_text to add language button."""
                if 'reply_markup' in kwargs:
                    kwargs['reply_markup'] = add_language_button(kwargs['reply_markup'])
                return original_reply_method(*args, **kwargs)
            
            update.message.reply_text = wrapped_reply
        
        try:
            # Call original show_main_menu
            result = original_main_menu(update, user_id)
            return result
        finally:
            # Restore original methods
            if original_edit_method and update.callback_query:
                update.callback_query.edit_message_text = original_edit_method
            if original_reply_method and hasattr(update, 'message') and update.message:
                update.message.reply_text = original_reply_method
    
    return wrapped_main_menu


def apply_menu_wrapper(bot_instance):
    """
    Apply the enhanced menu wrapper to a bot instance.
    
    This function patches the bot's show_main_menu method with our wrapper.
    
    Args:
        bot_instance: EnhancedBot instance to patch
    """
    if hasattr(bot_instance, 'show_main_menu'):
        original_method = bot_instance.show_main_menu
        wrapped_method = wrap_main_menu(original_method)
        
        # Replace the method using descriptor protocol
        bot_instance.show_main_menu = wrapped_method.__get__(bot_instance, type(bot_instance))
        
        logger.info("✅ Main menu (show_main_menu) wrapped with enhanced language support")
    else:
        logger.warning("⚠️ Bot instance does not have show_main_menu method")
