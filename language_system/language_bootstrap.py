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
        print("🔧 bootstrap_language_system: 开始启动...")
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
        print("🔧 bootstrap_language_system: 初始化 language manager...")
        lang_manager = get_language_manager()
        logger.info(f"✅ Language manager initialized with {len(lang_manager.supported_languages)} languages")
        print(f"✅ Language manager initialized with {len(lang_manager.supported_languages)} languages")
        
        # 2. Initialize middleware
        print("🔧 bootstrap_language_system: 初始化 middleware...")
        middleware = get_middleware()
        logger.info("✅ Language middleware initialized")
        print("✅ Language middleware initialized")
        
        # 3. Setup integration (registers handlers)
        print("🔧 bootstrap_language_system: 设置 integration...")
        integration = setup_language_integration(bot_instance)
        logger.info("✅ Language integration setup complete")
        print("✅ Language integration setup complete")
        
        # 4. Apply enhanced language button fix
        print("🔧 bootstrap_language_system: 应用 button fix...")
        apply_language_button_fix(bot_instance)
        logger.info("✅ Enhanced language button fix applied")
        print("✅ Enhanced language button fix applied")
        
        # 5. Verify callback handlers are registered
        print("🔧 bootstrap_language_system: 验证 handlers...")
        verify_callback_handlers(bot_instance)
        logger.info("✅ Callback handlers verified")
        print("✅ Callback handlers verified")
        
        logger.info("🌐 ===== Language System Bootstrap Complete =====")
        logger.info(f"🌐 Supported languages: {', '.join(lang_manager.supported_languages)}")
        logger.info("🌐 =============================================")
        print("🌐 ===== Language System Bootstrap Complete =====")
        print(f"🌐 Supported languages: {', '.join(lang_manager.supported_languages)}")
        print("🌐 =============================================")
        
        return True
        
    except Exception as e:
        print(f"❌ bootstrap_language_system 失败: {e}")
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
    
    NOTE: This function should be called from main() in tdata.py.
    """
    try:
        import sys
        
        print("🔧 inject_language_system: 开始注入...")
        
        # Get the tdata module from sys.modules
        # When run as script (__name__ == '__main__'), the module is in sys.modules['__main__']
        # When imported, it's in sys.modules['tdata']
        tdata = None
        
        # Try to get from sys.modules as 'tdata' first
        if 'tdata' in sys.modules:
            tdata = sys.modules['tdata']
            print("🔧 inject_language_system: 从 sys.modules['tdata'] 获取 ✓")
        # If not found, try '__main__' (when run as script)
        elif '__main__' in sys.modules:
            tdata = sys.modules['__main__']
            print("🔧 inject_language_system: 从 sys.modules['__main__'] 获取 ✓")
        
        if tdata is None:
            print("⚠️ inject_language_system: tdata 不在 sys.modules")
            logger.warning("⚠️ tdata module not in sys.modules - injection must be called from main()")
            return False
        
        # Get the EnhancedBot class
        if not hasattr(tdata, 'EnhancedBot'):
            print("⚠️ inject_language_system: 模块中未找到 EnhancedBot 类")
            logger.warning("⚠️ EnhancedBot class not found in module")
            return False
        
        print("🔧 inject_language_system: 找到 EnhancedBot 类 ✓")
        EnhancedBot = tdata.EnhancedBot
        
        # Check if already wrapped (to avoid double-wrapping)
        if hasattr(EnhancedBot.__init__, '_language_wrapped'):
            print("⚠️ inject_language_system: EnhancedBot.__init__ 已经被包装，跳过")
            logger.info("⚠️ EnhancedBot.__init__ already wrapped, skipping")
            return True
        
        original_init = EnhancedBot.__init__
        
        def wrapped_init(self, *args, **kwargs):
            # Call original __init__
            original_init(self, *args, **kwargs)
            
            # Bootstrap language system (with graceful failure handling)
            print("🌐 Starting language system bootstrap...")
            logger.info("🌐 Starting language system bootstrap...")
            try:
                success = bootstrap_language_system(self)
                if not success:
                    print("⚠️ Language system bootstrap failed")
                    logger.warning("⚠️ Language system bootstrap failed, bot will continue without language support")
                else:
                    print("✅ Language system bootstrap successful")
            except Exception as e:
                print(f"❌ Language system bootstrap error: {e}")
                logger.error(f"❌ Language system bootstrap error: {e}")
                logger.warning("⚠️ Bot will continue without language support")
                import traceback
                traceback.print_exc()
                # Don't re-raise - allow bot to continue
        
        # Mark as wrapped to avoid double-wrapping
        wrapped_init._language_wrapped = True
        
        # Replace __init__
        EnhancedBot.__init__ = wrapped_init
        
        print("✅ inject_language_system: __init__ 包装完成 ✓")
        logger.info("✅ Language system injection complete")
        return True
        
    except Exception as e:
        print(f"❌ inject_language_system 失败: {e}")
        logger.error(f"❌ Failed to inject language system: {e}")
        logger.warning("⚠️ Bot will start without language support")
        import traceback
        traceback.print_exc()
        return False


# DO NOT auto-inject when this module is imported!
# Instead, tdata.py will call inject_language_system() explicitly after EnhancedBot is defined
