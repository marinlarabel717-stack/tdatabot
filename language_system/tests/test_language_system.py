#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for language system
Tests the basic functionality without requiring a running bot
"""

import os
import sys
import tempfile
import sqlite3

# Add parent directory (language_system) to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("🧪 Testing Language System")
print("=" * 50)

# Test 1: Language Manager
print("\n1️⃣ Testing Language Manager...")
try:
    from language_manager import LanguageManager
    
    # Update lang_dir path to point to correct location
    lang_dir = os.path.join(parent_dir, "lang")
    lang_manager = LanguageManager(lang_dir=lang_dir, default_lang="en")
    
    # Check supported languages
    print(f"   Supported languages: {lang_manager.supported_languages}")
    assert 'en' in lang_manager.supported_languages, "English not loaded"
    assert 'zh' in lang_manager.supported_languages, "Chinese not loaded"
    
    # Test translation
    en_welcome = lang_manager.get('menu.welcome', lang='en')
    print(f"   EN: {en_welcome}")
    
    zh_welcome = lang_manager.get('menu.welcome', lang='zh')
    print(f"   ZH: {zh_welcome}")
    
    # Test fallback
    missing = lang_manager.get('nonexistent.key', lang='en')
    print(f"   Fallback test: {missing}")
    
    # Test nested keys
    status = lang_manager.get('status.version', lang='en')
    print(f"   Nested key: {status}")
    
    print("   ✅ Language Manager working correctly")
except Exception as e:
    print(f"   ❌ Language Manager test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Language Middleware
print("\n2️⃣ Testing Language Middleware...")
try:
    from language_middleware import LanguageMiddleware
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    
    try:
        middleware = LanguageMiddleware(db_path=test_db)
        
        # Test setting language
        test_user_id = 12345
        success = middleware.set_user_language(test_user_id, 'zh')
        assert success, "Failed to set language"
        print("   ✅ Set language successful")
        
        # Test getting language
        lang = middleware.get_user_language(test_user_id)
        assert lang == 'zh', f"Expected 'zh', got '{lang}'"
        print(f"   ✅ Get language successful: {lang}")
        
        # Test translation for user
        text = middleware.translate_for_user(test_user_id, 'menu.welcome')
        print(f"   ✅ User translation: {text}")
        
        # Test default language for new user
        new_user_lang = middleware.get_user_language(99999)
        assert new_user_lang == 'en', f"Expected 'en', got '{new_user_lang}'"
        print(f"   ✅ Default language for new user: {new_user_lang}")
        
        print("   ✅ Language Middleware working correctly")
    finally:
        # Cleanup
        if os.path.exists(test_db):
            os.unlink(test_db)
except Exception as e:
    print(f"   ❌ Language Middleware test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Database Table Creation
print("\n3️⃣ Testing Database Table...")
try:
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        test_db = f.name
    
    try:
        from language_middleware import LanguageMiddleware
        
        middleware = LanguageMiddleware(db_path=test_db)
        
        # Verify table exists
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_language'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "Table not created"
        print("   ✅ Database table created successfully")
    finally:
        if os.path.exists(test_db):
            os.unlink(test_db)
except Exception as e:
    print(f"   ❌ Database table test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Translation Files
print("\n4️⃣ Testing Translation Files...")
try:
    import json
    
    lang_dir = "lang"
    
    for lang_file in ['en.json', 'zh.json']:
        file_path = os.path.join(lang_dir, lang_file)
        
        if not os.path.exists(file_path):
            print(f"   ⚠️ File not found: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required keys
        required_keys = ['menu', 'language', 'status', 'common']
        for key in required_keys:
            assert key in data, f"Missing required key: {key} in {lang_file}"
        
        print(f"   ✅ {lang_file}: Valid JSON with required keys")
    
    print("   ✅ All translation files are valid")
except Exception as e:
    print(f"   ❌ Translation file test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Import Test
print("\n5️⃣ Testing Module Imports...")
try:
    # Test all imports
    modules = [
        'language_manager',
        'language_middleware',
        'language_integration',
        'menu_wrapper',
        'language_bootstrap'
    ]
    
    for module_name in modules:
        __import__(module_name)
        print(f"   ✅ {module_name} imports successfully")
    
    print("   ✅ All modules import successfully")
except Exception as e:
    print(f"   ❌ Module import test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 50)
print("🎉 Language System Test Complete!")
print("=" * 50)
print("\n📝 To start the bot with language support:")
print("   python start_with_language.py")
print("\n📚 For more information, see LANGUAGE_SYSTEM.md")
