#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language Integration Module for TDataBot
Non-intrusive integration of language switching functionality
"""

import logging
from typing import Optional, Any

# Import telegram modules if available (optional for testing)
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import CallbackContext, CallbackQueryHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    Update = object
    InlineKeyboardButton = object
    InlineKeyboardMarkup = object
    CallbackContext = object
    CallbackQueryHandler = object
    TELEGRAM_AVAILABLE = False
    Any = object

# Import modules - try relative import first, then absolute
try:
    from .language_manager import get_language_manager
    from .language_middleware import get_middleware
except ImportError:
    from language_manager import get_language_manager
    from language_middleware import get_middleware

logger = logging.getLogger(__name__)


class LanguageIntegration:
    """
    Non-intrusive language integration system.
    
    This class provides methods to extend the bot's functionality
    with language switching without modifying the original code.
    """
    
    def __init__(self, bot_instance):
        """
        Initialize language integration.
        
        Args:
            bot_instance: Reference to the EnhancedBot instance
        """
        self.bot = bot_instance
        self.lang_manager = get_language_manager()
        self.middleware = get_middleware()
        
        # Register language-related handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register callback handlers for language switching."""
        # Create language selection handler
        lang_select_handler = CallbackQueryHandler(
            self.handle_language_select,
            pattern=r'^lang_select$'
        )
        
        # Create language change handler
        lang_change_handler = CallbackQueryHandler(
            self.handle_language_change,
            pattern=r'^lang_set_\w+$'
        )
        
        # Insert handlers BEFORE the catch-all CallbackQueryHandler
        # Find the position of the catch-all handler (the one without a pattern)
        dispatcher = self.bot.updater.dispatcher
        
        # Get handlers for group 0 (default group)
        handlers_list = dispatcher.handlers.get(0, [])
        
        # Find the index of the first CallbackQueryHandler without a pattern
        catch_all_index = None
        for i, handler in enumerate(handlers_list):
            if isinstance(handler, CallbackQueryHandler) and handler.pattern is None:
                catch_all_index = i
                break
        
        # If we found a catch-all handler, insert our handlers before it
        if catch_all_index is not None:
            handlers_list.insert(catch_all_index, lang_select_handler)
            handlers_list.insert(catch_all_index + 1, lang_change_handler)
            logger.info(f"✅ Language handlers inserted at position {catch_all_index} (before catch-all)")
        else:
            # Otherwise, just add them normally (they'll be at the end)
            dispatcher.add_handler(lang_select_handler)
            dispatcher.add_handler(lang_change_handler)
            logger.info("✅ Language handlers registered at end (no catch-all found)")
        
        logger.info("✅ Language handlers registered")
    
    def handle_language_select(self, update: Update, context: CallbackContext):
        """
        Handle language selection menu request.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        current_lang = self.middleware.get_user_language(user_id)
        
        # Create language selection buttons
        buttons = []
        for lang_code in self.lang_manager.supported_languages:
            lang_name = self.lang_manager.get_language_name(lang_code)
            
            # Add checkmark for current language
            if lang_code == current_lang:
                lang_name = f"✅ {lang_name}"
            
            buttons.append([
                InlineKeyboardButton(
                    lang_name,
                    callback_data=f"lang_set_{lang_code}"
                )
            ])
        
        # Add back button
        back_text = self.middleware.translate_for_user(
            user_id, 
            "menu.back_to_main"
        )
        buttons.append([
            InlineKeyboardButton(back_text, callback_data="back_to_main")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        # Get prompt text in user's current language
        prompt_text = self.middleware.translate_for_user(
            user_id,
            "language.select_prompt"
        )
        
        try:
            query.edit_message_text(
                text=prompt_text,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"❌ Failed to show language menu: {e}")
    
    def handle_language_change(self, update: Update, context: CallbackContext):
        """
        Handle language change request.
        
        Args:
            update: Telegram update object
            context: Callback context
        """
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        
        # Extract language code from callback data
        callback_data = query.data
        lang_code = callback_data.replace("lang_set_", "")
        
        # Validate language code
        if lang_code not in self.lang_manager.supported_languages:
            logger.warning(f"Invalid language code: {lang_code}")
            return
        
        # Set user's language preference
        success = self.middleware.set_user_language(user_id, lang_code)
        
        if success:
            # Show confirmation message in new language
            confirmation = self.middleware.translate_for_user(
                user_id,
                "language.changed"
            )
            
            try:
                query.edit_message_text(text=confirmation)
            except Exception as e:
                logger.error(f"❌ Failed to show confirmation: {e}")
            
            # Schedule main menu refresh by sending a NEW message
            # Don't try to edit the old message - the query expires!
            stored_user_id = user_id
            stored_chat_id = query.message.chat_id if query.message else None
            
            try:
                # Use context.job_queue to schedule a non-blocking callback
                if hasattr(context, 'job_queue') and context.job_queue and stored_chat_id:
                    def refresh_callback(ctx):
                        """Callback to send fresh menu message."""
                        try:
                            # Send a fresh menu message instead of trying to edit
                            # Get menu text and keyboard
                            menu_text = self.middleware.translate_for_user(
                                stored_user_id,
                                "menu.welcome"
                            )
                            
                            # Call the bot's show_main_menu but with a fresh message send
                            # We'll send a new message instead of editing
                            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
                            
                            # Create menu keyboard (simplified version)
                            # The actual menu will be created by show_main_menu wrapper
                            # For now, just send a simple new menu message
                            self.bot.updater.bot.send_message(
                                chat_id=stored_chat_id,
                                text=menu_text,
                                reply_markup=None  # Will be added by wrappers
                            )
                            logger.info("✅ Fresh menu message sent successfully")
                        except Exception as e:
                            logger.error(f"❌ Failed to send fresh menu: {e}")
                    
                    context.job_queue.run_once(
                        refresh_callback,
                        1.0,  # 1 second delay
                    )
                    logger.info("📅 Menu refresh scheduled (will send new message)")
                else:
                    # Fallback: log that refresh isn't available
                    logger.info("⚠️ job_queue not available, menu will refresh on next interaction")
            except Exception as e:
                logger.error(f"❌ Failed to schedule menu refresh: {e}")
        else:
            logger.error("❌ Failed to change language")
    
    def _refresh_main_menu(self, update: Update, user_id: int):
        """Helper method to refresh main menu (used as callback)."""
        try:
            self.bot.show_main_menu(update, user_id)
        except Exception as e:
            logger.error(f"❌ Failed to refresh main menu: {e}")
    
    def get_extended_menu_buttons(self, user_id: int, original_buttons: list) -> list:
        """
        Extend original menu buttons with language selection.
        
        Args:
            user_id: Telegram user ID
            original_buttons: Original button list
            
        Returns:
            Extended button list with language option
        """
        # Create a copy of original buttons
        extended_buttons = list(original_buttons)
        
        # Get language button text
        lang_text = self.middleware.translate_for_user(
            user_id,
            "menu.select_language"
        )
        
        # Add language selection button before the status button
        # Find where to insert (before the last button typically)
        insert_position = len(extended_buttons) - 1 if extended_buttons else 0
        
        extended_buttons.insert(insert_position, [
            InlineKeyboardButton(lang_text, callback_data="lang_select")
        ])
        
        return extended_buttons
    
    def translate_welcome_text(self, user_id: int) -> str:
        """
        Get translated welcome text for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Translated welcome text
        """
        welcome = self.middleware.translate_for_user(user_id, "menu.welcome")
        return welcome


# Global integration instance
_integration: Optional[LanguageIntegration] = None


def setup_language_integration(bot_instance) -> LanguageIntegration:
    """
    Setup language integration for the bot.
    
    Args:
        bot_instance: EnhancedBot instance
        
    Returns:
        LanguageIntegration instance
    """
    global _integration
    if _integration is None:
        _integration = LanguageIntegration(bot_instance)
        logger.info("🌐 Language integration initialized")
    return _integration


def get_integration() -> Optional[LanguageIntegration]:
    """
    Get the global language integration instance.
    
    Returns:
        LanguageIntegration instance or None
    """
    return _integration
