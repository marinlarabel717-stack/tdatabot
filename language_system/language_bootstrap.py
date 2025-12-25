#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language System Bootstrap
This module initializes the language system and patches the bot
"""

import logging

logger = logging.getLogger(__name__)


def bootstrap_language_system(bot_instance):
    """
    Bootstrap the complete language system for the bot.
    
    This function:
    1. Initializes the language manager
    2. Sets up the middleware
    3. Registers language handlers
    4. Wraps the main menu
    
    Args:
        bot_instance: EnhancedBot instance to enhance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import modules - try relative import first, then absolute
        try:
            from .language_manager import get_language_manager
            from .language_middleware import get_middleware
            from .language_integration import setup_language_integration
            from .language_button_fix import apply_language_button_fix, verify_callback_handlers
        except ImportError:
            from language_manager import get_language_manager
            from language_middleware import get_middleware
            from language_integration import setup_language_integration
            from language_button_fix import apply_language_button_fix, verify_callback_handlers
        
        # 1. Initialize language manager
        lang_manager = get_language_manager()
        logger.info(f"✅ Language manager initialized with {len(lang_manager.supported_languages)} languages")
        
        # 2. Initialize middleware
        middleware = get_middleware()
        logger.info("✅ Language middleware initialized")
        
        # 3. Setup integration (registers handlers)
        integration = setup_language_integration(bot_instance)
        logger.info("✅ Language integration setup complete")
        
        # 4. Apply enhanced language button fix
        apply_language_button_fix(bot_instance)
        logger.info("✅ Enhanced language button fix applied")
        
        # 5. Verify callback handlers are registered
        verify_callback_handlers(bot_instance)
        logger.info("✅ Callback handlers verified")
        
        logger.info("🌐 ===== Language System Bootstrap Complete =====")
        logger.info(f"🌐 Supported languages: {', '.join(lang_manager.supported_languages)}")
        logger.info("🌐 =============================================")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to bootstrap language system: {e}")
        import traceback
        traceback.print_exc()
        return False


def inject_language_system():
    """
    Inject the language system into the bot startup process.
    
    This function patches the EnhancedBot.__init__ method to automatically
    initialize the language system when the bot starts.
    
    Handles failures gracefully - if language system fails to load,
    the bot will still start normally without language support.
    """
    try:
        # Add parent directory to path to import tdata
        import os
        import sys
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import the main module
        import tdata
        
        # Get the EnhancedBot class
        if not hasattr(tdata, 'EnhancedBot'):
            logger.warning("⚠️ EnhancedBot class not found")
            return False
        
        EnhancedBot = tdata.EnhancedBot
        original_init = EnhancedBot.__init__
        
        def wrapped_init(self, *args, **kwargs):
            # Call original __init__
            original_init(self, *args, **kwargs)
            
            # Bootstrap language system (with graceful failure handling)
            logger.info("🌐 Starting language system bootstrap...")
            try:
                success = bootstrap_language_system(self)
                if not success:
                    logger.warning("⚠️ Language system bootstrap failed, bot will continue without language support")
            except Exception as e:
                logger.error(f"❌ Language system bootstrap error: {e}")
                logger.warning("⚠️ Bot will continue without language support")
                import traceback
                traceback.print_exc()
                # Don't re-raise - allow bot to continue
        
        # Replace __init__
        EnhancedBot.__init__ = wrapped_init
        
        logger.info("✅ Language system injection complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to inject language system: {e}")
        logger.warning("⚠️ Bot will start without language support")
        import traceback
        traceback.print_exc()
        return False


# Auto-inject when this module is imported
if __name__ != "__main__":
    # Only inject if not running as main script
    inject_language_system()
