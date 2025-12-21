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
        # Language selection handler
        self.bot.updater.dispatcher.add_handler(
            CallbackQueryHandler(
                self.handle_language_select,
                pattern=r'^lang_select$'
            )
        )
        
        # Language change handler
        self.bot.updater.dispatcher.add_handler(
            CallbackQueryHandler(
                self.handle_language_change,
                pattern=r'^lang_set_\w+$'
            )
        )
        
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
            
            # Schedule main menu refresh using callback context
            # Store necessary information to avoid stale objects
            stored_user_id = user_id
            stored_chat_id = query.message.chat_id if query.message else None
            stored_message_id = query.message.message_id if query.message else None
            
            try:
                # Use context.job_queue to schedule a non-blocking callback
                if hasattr(context, 'job_queue') and context.job_queue and stored_chat_id:
                    def refresh_callback(ctx):
                        """Callback to refresh menu with correct method."""
                        try:
                            # Create a minimal Update object for the callback
                            # We only need the callback_query with message info
                            from telegram import Message, Chat, CallbackQuery
                            
                            # Create minimal objects needed for show_main_menu
                            chat = Chat(id=stored_chat_id, type='private')
                            message = Message(
                                message_id=stored_message_id,
                                date=None,
                                chat=chat
                            )
                            callback_query = CallbackQuery(
                                id=str(stored_message_id),
                                from_user=query.from_user,
                                chat_instance='',
                                message=message,
                                bot=query.bot
                            )
                            
                            # Create new Update with fresh callback_query
                            from telegram import Update as TelegramUpdate
                            fresh_update = TelegramUpdate(
                                update_id=0,
                                callback_query=callback_query
                            )
                            
                            # Call show_main_menu with fresh update
                            self.bot.show_main_menu(fresh_update, stored_user_id)
                        except Exception as e:
                            logger.error(f"❌ Failed to refresh main menu in callback: {e}")
                            # Log but don't crash - menu is already in selected language
                    
                    context.job_queue.run_once(
                        refresh_callback,
                        1.0,  # 1 second delay
                    )
                    logger.info("📅 Menu refresh scheduled (non-blocking)")
                else:
                    # Fallback: immediate refresh if job_queue not available
                    logger.info("⚠️ job_queue not available, immediate refresh")
                    self.bot.show_main_menu(update, user_id)
            except Exception as e:
                logger.error(f"❌ Failed to schedule menu refresh: {e}")
                # Try immediate refresh as final fallback
                try:
                    self.bot.show_main_menu(update, user_id)
                except Exception as e2:
                    logger.error(f"❌ Failed to refresh main menu: {e2}")
                    # Language was already changed, just log the error
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
