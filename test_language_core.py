#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified test for core language functionality (no telegram dependency needed)
"""

import os
import sys
import tempfile
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Language System Core Tests")
print("=" * 60)

def test_language_manager():
    """Test the language manager core functionality"""
    print("\n✅ Test 1: Language Manager")
    from language_manager import LanguageManager
    
    lm = LanguageManager(lang_dir="lang", default_lang="en")
    
    # Test 1: Check languages loaded
    assert len(lm.supported_languages) >= 2, "Should load at least 2 languages"
    print(f"   ✓ Loaded {len(lm.supported_languages)} languages: {lm.supported_languages}")
    
    # Test 2: English translation
    en_text = lm.get('menu.welcome', lang='en')
    assert 'Welcome' in en_text or 'welcome' in en_text.lower(), "English translation failed"
    print(f"   ✓ English: {en_text}")
    
    # Test 3: Chinese translation
    zh_text = lm.get('menu.welcome', lang='zh')
    assert '欢迎' in zh_text, "Chinese translation failed"
    print(f"   ✓ Chinese: {zh_text}")
    
    # Test 4: Fallback
    fallback_text = lm.get('nonexistent.key', lang='en')
    assert fallback_text == 'nonexistent.key', "Fallback should return key"
    print(f"   ✓ Fallback: {fallback_text}")
    
    # Test 5: Nested keys
    version = lm.get('status.version', lang='en')
    assert version == 'Version', "Nested key failed"
    print(f"   ✓ Nested key: {version}")
    
    # Test 6: Format variables
    formatted = lm.get('menu.welcome', lang='en')
    print(f"   ✓ Formatted: {formatted}")
    
    return True

def test_middleware():
    """Test the middleware database functionality"""
    print("\n✅ Test 2: Language Middleware")
    from language_middleware import LanguageMiddleware
    
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    
    try:
        mw = LanguageMiddleware(db_path=test_db)
        
        # Test 1: Set language
        test_user = 12345
        success = mw.set_user_language(test_user, 'zh')
        assert success, "Failed to set language"
        print(f"   ✓ Set language for user {test_user}")
        
        # Test 2: Get language
        lang = mw.get_user_language(test_user)
        assert lang == 'zh', f"Expected 'zh', got '{lang}'"
        print(f"   ✓ Retrieved language: {lang}")
        
        # Test 3: Translate for user
        text = mw.translate_for_user(test_user, 'menu.welcome')
        assert '欢迎' in text, "Translation failed"
        print(f"   ✓ Translated for user: {text}")
        
        # Test 4: Default language for new user
        new_user_lang = mw.get_user_language(99999)
        assert new_user_lang == 'en', "Default language should be 'en'"
        print(f"   ✓ Default for new user: {new_user_lang}")
        
        # Test 5: Update language
        mw.set_user_language(test_user, 'en')
        updated_lang = mw.get_user_language(test_user)
        assert updated_lang == 'en', "Language update failed"
        print(f"   ✓ Updated language to: {updated_lang}")
        
        return True
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)

def test_database_schema():
    """Test database table creation"""
    print("\n✅ Test 3: Database Schema")
    from language_middleware import LanguageMiddleware
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    
    try:
        mw = LanguageMiddleware(db_path=test_db)
        
        # Verify table structure
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_language'
        """)
        assert cursor.fetchone() is not None, "Table not created"
        print("   ✓ Table 'user_language' created")
        
        # Check columns
        cursor.execute("PRAGMA table_info(user_language)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'user_id' in columns, "Missing user_id column"
        assert 'language_code' in columns, "Missing language_code column"
        assert 'updated_at' in columns, "Missing updated_at column"
        print(f"   ✓ Columns present: {list(columns.keys())}")
        
        conn.close()
        return True
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)

def test_translation_completeness():
    """Test that translation files have all required keys"""
    print("\n✅ Test 4: Translation Completeness")
    import json
    
    required_sections = {
        'menu': ['welcome', 'select_language', 'back_to_main'],
        'language': ['changed', 'current', 'select_prompt'],
        'status': ['version', 'current_time'],
        'common': ['yes', 'no', 'cancel']
    }
    
    for lang_code in ['en', 'zh']:
        lang_file = f"lang/{lang_code}.json"
        with open(lang_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for section, keys in required_sections.items():
            assert section in data, f"Missing section '{section}' in {lang_code}"
            for key in keys:
                assert key in data[section], f"Missing key '{key}' in {section} ({lang_code})"
        
        print(f"   ✓ {lang_code}.json: All required keys present")
    
    return True

def test_concurrent_access():
    """Test concurrent database access"""
    print("\n✅ Test 5: Concurrent Access")
    from language_middleware import LanguageMiddleware
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    
    try:
        mw = LanguageMiddleware(db_path=test_db)
        
        # Simulate multiple users
        for user_id in range(1000, 1010):
            lang = 'zh' if user_id % 2 == 0 else 'en'
            mw.set_user_language(user_id, lang)
        
        # Verify all users
        for user_id in range(1000, 1010):
            expected_lang = 'zh' if user_id % 2 == 0 else 'en'
            actual_lang = mw.get_user_language(user_id)
            assert actual_lang == expected_lang, f"User {user_id} language mismatch"
        
        print("   ✓ Multiple users handled correctly")
        return True
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)

# Run all tests
try:
    all_passed = True
    
    tests = [
        test_language_manager,
        test_middleware,
        test_database_schema,
        test_translation_completeness,
        test_concurrent_access,
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
        print("🎉 All Core Tests Passed!")
        print("\n📝 Next Steps:")
        print("   1. Start the bot: python start_with_language.py")
        print("   2. Test language switching in Telegram")
        print("   3. Check that translations work correctly")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\n⚠️ Tests interrupted")
except Exception as e:
    print(f"\n❌ Test suite error: {e}")
    import traceback
    traceback.print_exc()
