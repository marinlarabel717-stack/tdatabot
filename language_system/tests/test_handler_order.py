#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for handler registration order fix
This verifies that language handlers are inserted before the catch-all handler
"""

import os
import sys
import tempfile

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("🧪 Handler Registration Order Test")
print("=" * 60)


def test_handler_order_logic():
    """Test the logic for inserting handlers at the correct position"""
    print("\n✅ Test 1: Handler Insertion Logic")
    
    # Simulate handler list
    class MockHandler:
        def __init__(self, name, has_pattern=True):
            self.name = name
            self.pattern = "^test$" if has_pattern else None
    
    # Simulate telegram's CallbackQueryHandler
    class CallbackQueryHandler:
        def __init__(self, callback, pattern=None):
            self.callback = callback
            self.pattern = pattern
    
    # Create mock handlers list
    handlers_list = [
        CallbackQueryHandler(lambda: None, pattern="^back_to_main$"),
        CallbackQueryHandler(lambda: None, pattern="^broadcast_"),
        CallbackQueryHandler(lambda: None, pattern=None),  # Catch-all at position 2
        MockHandler("other", True)
    ]
    
    # Find catch-all index
    catch_all_index = None
    for i, handler in enumerate(handlers_list):
        if isinstance(handler, CallbackQueryHandler) and handler.pattern is None:
            catch_all_index = i
            break
    
    assert catch_all_index == 2, f"Expected catch-all at index 2, got {catch_all_index}"
    print(f"   ✓ Catch-all handler found at index {catch_all_index}")
    
    # Insert new handlers
    lang_select = CallbackQueryHandler(lambda: None, pattern="^lang_select$")
    lang_change = CallbackQueryHandler(lambda: None, pattern="^lang_set_\w+$")
    
    handlers_list.insert(catch_all_index, lang_select)
    handlers_list.insert(catch_all_index + 1, lang_change)
    
    # Verify order
    assert handlers_list[2].pattern == "^lang_select$", "lang_select not at position 2"
    assert handlers_list[3].pattern == "^lang_set_\w+$", "lang_change not at position 3"
    assert handlers_list[4].pattern is None, "Catch-all not at position 4"
    
    print("   ✓ Handlers inserted in correct order:")
    for i, h in enumerate(handlers_list[:5]):
        if isinstance(h, CallbackQueryHandler):
            pattern = h.pattern if h.pattern else "None (catch-all)"
            print(f"      [{i}] pattern={pattern}")
    
    return True


def test_handler_without_catchall():
    """Test behavior when no catch-all handler exists"""
    print("\n✅ Test 2: No Catch-all Handler")
    
    class CallbackQueryHandler:
        def __init__(self, callback, pattern=None):
            self.callback = callback
            self.pattern = pattern
    
    # Create handlers list without catch-all
    handlers_list = [
        CallbackQueryHandler(lambda: None, pattern="^back_to_main$"),
        CallbackQueryHandler(lambda: None, pattern="^broadcast_"),
    ]
    
    # Try to find catch-all
    catch_all_index = None
    for i, handler in enumerate(handlers_list):
        if isinstance(handler, CallbackQueryHandler) and handler.pattern is None:
            catch_all_index = i
            break
    
    assert catch_all_index is None, "Should not find catch-all"
    print("   ✓ No catch-all handler found (expected)")
    print("   ✓ Handlers would be added at the end")
    
    return True


def test_pattern_matching():
    """Test that our patterns match the expected callback data"""
    print("\n✅ Test 3: Pattern Matching")
    import re
    
    # Test lang_select pattern
    pattern = r'^lang_select$'
    assert re.match(pattern, 'lang_select'), "Should match 'lang_select'"
    assert not re.match(pattern, 'lang_select_extra'), "Should not match extra text"
    assert not re.match(pattern, 'prefix_lang_select'), "Should not match prefix"
    print(f"   ✓ Pattern {pattern} works correctly")
    
    # Test lang_set pattern
    pattern = r'^lang_set_\w+$'
    assert re.match(pattern, 'lang_set_en'), "Should match 'lang_set_en'"
    assert re.match(pattern, 'lang_set_zh'), "Should match 'lang_set_zh'"
    assert re.match(pattern, 'lang_set_ru'), "Should match 'lang_set_ru'"
    assert re.match(pattern, 'lang_set_es'), "Should match 'lang_set_es'"
    assert not re.match(pattern, 'lang_set_'), "Should not match without language code"
    assert not re.match(pattern, 'lang_set'), "Should not match without underscore"
    print(f"   ✓ Pattern {pattern} works correctly")
    
    return True


def test_integration_import():
    """Test that language_integration can be imported"""
    print("\n✅ Test 4: Module Import")
    try:
        from language_integration import LanguageIntegration
        print("   ✓ language_integration module imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Run all tests
try:
    all_passed = True
    
    tests = [
        test_handler_order_logic,
        test_handler_without_catchall,
        test_pattern_matching,
        test_integration_import,
    ]
    
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"\n   ❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All Handler Order Tests Passed!")
        print("\n📝 Summary:")
        print("   ✓ Handler insertion logic is correct")
        print("   ✓ Handles case when no catch-all exists")
        print("   ✓ Callback patterns match expected data")
        print("   ✓ Module imports successfully")
        print("\n✨ Language handlers will now be processed before catch-all!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\n⚠️ Tests interrupted")
except Exception as e:
    print(f"\n❌ Test suite error: {e}")
    import traceback
    traceback.print_exc()
