#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Button Fix Module
This module patches the show_main_menu method to ensure:
1. The language button is added properly with translated text
2. No duplicate buttons are created
3. All callbacks work correctly
4. Works for both callback queries and fresh messages

This is a non-intrusive fix that wraps the existing functionality.
"""

import logging
from functools import wraps
from typing import Callable

# Import telegram modules if available
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

# Import middleware
try:
    from .language_middleware import get_middleware
except ImportError:
    from language_middleware import get_middleware

logger = logging.getLogger(__name__)


def create_enhanced_menu_wrapper(original_method: Callable) -> Callable:
    """
    Create an enhanced wrapper that ensures proper language button handling.
    
    This wrapper:
    1. Removes any manually added language buttons from tdata.py
    2. Adds a single, properly translated language button
    3. Handles both callback queries and fresh messages
    4. Ensures callbacks are properly attached
    
    Args:
        original_method: The original show_main_menu method
        
    Returns:
        Enhanced wrapped method
    """
    @wraps(original_method)
    def enhanced_show_main_menu(self, update: Update, user_id: int):
        """
        Enhanced show_main_menu with proper language button support.
        """
        # Validate user_id
        if user_id is None:
            if update.effective_user:
                user_id = update.effective_user.id
            elif update.callback_query and update.callback_query.from_user:
                user_id = update.callback_query.from_user.id
            else:
                return original_method(update, user_id)
        
        # Get middleware for translations
        middleware = get_middleware()
        
        # Track wrapped methods for cleanup
        wrapped_methods = []
        
        def add_language_button_to_keyboard(keyboard):
            """
            Add language button to keyboard, removing duplicates if they exist.
            
            Args:
                keyboard: InlineKeyboardMarkup to modify
                
            Returns:
                Modified InlineKeyboardMarkup with language button
            """
            if not isinstance(keyboard, InlineKeyboardMarkup):
                return keyboard
            
            # Get button rows
            buttons = list(keyboard.inline_keyboard)
            
            # Remove any existing language buttons (to avoid duplicates)
            buttons = [
                row for row in buttons
                if not any(btn.callback_data == "lang_select" for btn in row)
            ]
            
            # Get translated button text for this user
            lang_button_text = middleware.translate_for_user(
                user_id,
                "menu.select_language"
            )
            
            # Create new language button
            lang_button = InlineKeyboardButton(
                lang_button_text,
                callback_data="lang_select"
            )
            
            # Insert before the last row (typically "Status" button)
            if buttons:
                insert_pos = len(buttons) - 1
                buttons.insert(insert_pos, [lang_button])
            else:
                buttons.append([lang_button])
            
            # Return new keyboard
            return InlineKeyboardMarkup(buttons)
        
        # Wrap callback query's edit_message_text if present
        if update.callback_query:
            query = update.callback_query
            original_edit = query.edit_message_text
            
            def wrapped_edit(*args, **kwargs):
                # Add language button to reply_markup
                if 'reply_markup' in kwargs:
                    kwargs['reply_markup'] = add_language_button_to_keyboard(
                        kwargs['reply_markup']
                    )
                return original_edit(*args, **kwargs)
            
            query.edit_message_text = wrapped_edit
            wrapped_methods.append(('callback_query', original_edit))
        
        # Wrap message.reply_text if present (for fresh messages)
        if hasattr(update, 'message') and update.message:
            original_reply = update.message.reply_text
            
            def wrapped_reply(*args, **kwargs):
                # Add language button to reply_markup
                if 'reply_markup' in kwargs:
                    kwargs['reply_markup'] = add_language_button_to_keyboard(
                        kwargs['reply_markup']
                    )
                return original_reply(*args, **kwargs)
            
            update.message.reply_text = wrapped_reply
            wrapped_methods.append(('message', original_reply))
        
        try:
            # Call the original method
            result = original_method(update, user_id)
            return result
        except Exception as e:
            logger.error(f"❌ Error in show_main_menu: {e}")
            raise
        finally:
            # Restore original methods
            for method_type, original in wrapped_methods:
                if method_type == 'callback_query' and update.callback_query:
                    update.callback_query.edit_message_text = original
                elif method_type == 'message' and hasattr(update, 'message') and update.message:
                    update.message.reply_text = original
    
    return enhanced_show_main_menu


def apply_language_button_fix(bot_instance):
    """
    Apply the enhanced language button fix to the bot.
    
    This function:
    1. Wraps the show_main_menu method with enhanced handling
    2. Ensures language button is properly added with translations
    3. Prevents duplicate buttons
    4. Works for all menu display scenarios
    
    Args:
        bot_instance: The EnhancedBot instance to patch
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not hasattr(bot_instance, 'show_main_menu'):
            logger.warning("⚠️ Bot instance doesn't have show_main_menu method")
            return False
        
        # Get the original method
        original_method = bot_instance.show_main_menu
        
        # Create enhanced wrapper
        enhanced_method = create_enhanced_menu_wrapper(original_method)
        
        # Replace the method
        bot_instance.show_main_menu = enhanced_method.__get__(
            bot_instance,
            type(bot_instance)
        )
        
        logger.info("✅ Enhanced language button fix applied to show_main_menu")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to apply language button fix: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_callback_handlers(bot_instance):
    """
    Verify that language callback handlers are properly registered.
    
    Args:
        bot_instance: The EnhancedBot instance
        
    Returns:
        bool: True if handlers are registered, False otherwise
    """
    try:
        if not hasattr(bot_instance, 'updater'):
            logger.warning("⚠️ Bot instance doesn't have updater")
            return False
        
        dispatcher = bot_instance.updater.dispatcher
        
        # Check for language handlers
        handler_patterns = ['lang_select', 'lang_set_']
        found_handlers = []
        
        for group in dispatcher.handlers.values():
            for handler in group:
                # Check if this is a CallbackQueryHandler
                if hasattr(handler, 'pattern'):
                    pattern_str = str(handler.pattern)
                    for pattern in handler_patterns:
                        if pattern in pattern_str:
                            found_handlers.append(pattern)
        
        if len(found_handlers) >= 2:
            logger.info(f"✅ Language handlers verified: {found_handlers}")
            return True
        else:
            logger.warning(f"⚠️ Some language handlers may be missing: {found_handlers}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to verify handlers: {e}")
        return False


# Auto-export key functions
__all__ = [
    'apply_language_button_fix',
    'verify_callback_handlers',
    'create_enhanced_menu_wrapper'
]
