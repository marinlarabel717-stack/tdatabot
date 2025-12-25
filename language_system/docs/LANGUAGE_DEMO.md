# Language System Demo

## Visual Flow

This document demonstrates the language switching functionality.

## User Experience Flow

### Step 1: Main Menu (English)
```
🤖 Welcome to the Telegram Account Detection Bot

┌─────────────────────────────────────────────┐
│  [🚀 Account Check] [🔄 Format Conversion]  │
│  [🔐 Change 2FA]    [📦 Batch Create]       │
│  [🔓 Forget 2FA]    [❌ Remove 2FA]         │
│  ...                                         │
│  [🌐 Select Language]  <- NEW!              │
│  [⚙️ Status]                                │
└─────────────────────────────────────────────┘
```

### Step 2: Language Selection Menu
```
🌐 Please select your language:

┌─────────────────────────────────────────────┐
│  [✅ English]  <- Current language          │
│  [中文]                                      │
│  [🔙 Back to Main Menu]                     │
└─────────────────────────────────────────────┘
```

### Step 3: After Selecting Chinese
```
✅ 语言已切换为中文

(Menu refreshes automatically)
```

### Step 4: Main Menu (Chinese)
```
🤖 欢迎使用Telegram账号检测机器人

┌─────────────────────────────────────────────┐
│  [🚀 账号检测]       [🔄 格式转换]           │
│  [🔐 修改2FA]        [📦 批量创建]           │
│  [🔓 忘记2FA]        [❌删除2FA]            │
│  ...                                         │
│  [🌐 选择语言]  <- Translated!              │
│  [⚙️ 状态]                                  │
└─────────────────────────────────────────────┘
```

## Technical Flow

```
┌──────────────────────────────────────────────────────────┐
│                    User Action                            │
│           Click "🌐 Select Language"                     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│              language_integration.py                      │
│    handle_language_select(update, context)                │
│                                                            │
│  1. Get user's current language                           │
│  2. Load available languages                              │
│  3. Create selection menu with checkmark on current       │
│  4. Display language options                              │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    User Action                            │
│              Select a language (e.g., 中文)              │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│              language_integration.py                      │
│    handle_language_change(update, context)                │
│                                                            │
│  1. Extract language code from callback                   │
│  2. Validate language code                                │
│  3. Update user preference in database                    │
│  4. Show confirmation in new language                     │
│  5. Refresh main menu                                     │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                language_middleware.py                     │
│         set_user_language(user_id, 'zh')                  │
│                                                            │
│  Database Update:                                         │
│  INSERT OR REPLACE INTO user_language                     │
│  (user_id, language_code, updated_at)                     │
│  VALUES (12345, 'zh', CURRENT_TIMESTAMP)                  │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                   menu_wrapper.py                         │
│         Wraps main_menu() to add language button          │
│                                                            │
│  1. Intercept main menu creation                          │
│  2. Get user's language preference                        │
│  3. Add "🌐 选择语言" button (in Chinese)                │
│  4. Return enhanced menu                                  │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    Result                                 │
│           Menu displayed in Chinese                       │
└──────────────────────────────────────────────────────────┘
```

## Database Schema

### user_language table

```sql
CREATE TABLE user_language (
    user_id       INTEGER PRIMARY KEY,  -- Telegram user ID
    language_code TEXT NOT NULL,        -- Language code (en, zh, etc.)
    updated_at    TIMESTAMP             -- When preference was set
);
```

### Example Data

| user_id | language_code | updated_at          |
|---------|---------------|---------------------|
| 12345   | zh            | 2025-12-21 14:30:00 |
| 67890   | en            | 2025-12-21 14:35:00 |
| 11111   | zh            | 2025-12-21 14:40:00 |

## File Structure

```
tdatabot/
├── tdata.py                    # Original bot (NOT modified)
├── start_with_language.py      # New launcher with language support
│
├── Language System:
│   ├── language_manager.py     # Translation management
│   ├── language_middleware.py  # User preferences & DB
│   ├── language_integration.py # Handler registration
│   ├── menu_wrapper.py         # Menu patching
│   └── language_bootstrap.py   # System initialization
│
├── Translation Files:
│   └── lang/
│       ├── en.json             # English translations
│       └── zh.json             # Chinese translations
│
├── Documentation:
│   ├── LANGUAGE_SYSTEM.md      # Technical documentation
│   ├── LANGUAGE_QUICKSTART.md  # Quick start guide
│   └── LANGUAGE_DEMO.md        # This file
│
└── Tests:
    ├── test_language_core.py   # Core functionality tests
    └── test_language_system.py # Full system tests
```

## Translation Example

### English (lang/en.json)
```json
{
  "menu": {
    "welcome": "🤖 Welcome to the Telegram Account Detection Bot",
    "select_language": "🌐 Select Language",
    "account_check": "🚀 Account Check"
  },
  "language": {
    "changed": "✅ Language changed to English",
    "current": "Current language: English"
  }
}
```

### Chinese (lang/zh.json)
```json
{
  "menu": {
    "welcome": "🤖 欢迎使用Telegram账号检测机器人",
    "select_language": "🌐 选择语言",
    "account_check": "🚀 账号检测"
  },
  "language": {
    "changed": "✅ 语言已切换为中文",
    "current": "当前语言：中文"
  }
}
```

## Code Examples

### Getting User's Language

```python
from language_middleware import get_middleware

middleware = get_middleware()
user_lang = middleware.get_user_language(user_id)
# Returns: 'en', 'zh', etc.
```

### Translating Text

```python
# Option 1: Using middleware (recommended)
text = middleware.translate_for_user(user_id, 'menu.welcome')

# Option 2: Direct translation
from language_manager import translate
text = translate('menu.welcome', lang='zh')
```

### Setting User Language

```python
# User clicks language button
middleware.set_user_language(user_id, 'zh')

# Automatic translation from this point on
welcome = middleware.translate_for_user(user_id, 'menu.welcome')
# Returns: "🤖 欢迎使用Telegram账号检测机器人"
```

## Non-Intrusive Design Proof

### What We DON'T Do:
❌ Modify `tdata.py`
❌ Change existing functions
❌ Alter database schema of existing tables
❌ Require code changes to existing handlers

### What We DO:
✅ Create new modules that wrap existing functionality
✅ Use Python's dynamic patching capabilities
✅ Add a new database table (doesn't affect existing ones)
✅ Register new callback handlers
✅ Intercept menu creation to add language button

### Example: Menu Wrapping

Before (original code in tdata.py - unchanged):
```python
def main_menu(self, update, context):
    buttons = [
        [InlineKeyboardButton("🚀 Account Check", callback_data="start_check")],
        ...
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text, reply_markup=keyboard)
```

After (wrapped by menu_wrapper.py - no changes to original):
```python
# menu_wrapper.py creates a wrapper
def wrapped_main_menu(self, update, context):
    # Call original function (which hasn't changed)
    # But intercept before sending to add language button
    ...
    buttons.insert(-1, [InlineKeyboardButton("🌐 Select Language")])
    ...
```

## Testing Checklist

✅ **Core Functionality**
- [x] Language files load correctly
- [x] Translations work for both languages
- [x] Fallback to default language works
- [x] Nested keys work (e.g., 'menu.welcome')

✅ **Database Operations**
- [x] Table created successfully
- [x] User preferences stored correctly
- [x] User preferences retrieved correctly
- [x] Concurrent access handled

✅ **Integration**
- [x] All modules import without errors
- [x] Bootstrap system initializes correctly
- [x] Menu wrapper applies successfully

✅ **User Experience**
- [ ] Language button appears in main menu
- [ ] Language selection menu displays
- [ ] Language changes persist
- [ ] Menu refreshes in new language

Note: Full UX testing requires running the bot with Telegram.

## Performance Considerations

- **Translation Loading**: Once at startup (minimal overhead)
- **Database Queries**: One per language change (cached in session)
- **Menu Wrapping**: Negligible overhead (Python method wrapping)
- **Memory Usage**: ~50KB for translation files

## Future Enhancements

Possible improvements:
1. Add more languages (Spanish, French, Russian, etc.)
2. Translate all bot messages (currently only menu)
3. Auto-detect language from Telegram settings
4. Add pluralization support
5. Support RTL languages
6. Add translation admin panel

## Support & Troubleshooting

If the language button doesn't appear:
1. Verify you're using `start_with_language.py`
2. Check logs for initialization errors
3. Run `python test_language_core.py` to verify setup

If translations are incorrect:
1. Check JSON files are valid
2. Verify language codes match
3. Check for missing keys

## Conclusion

The language system provides seamless multi-language support without modifying the original bot code. It's designed to be:
- **Non-intrusive**: No changes to existing code
- **Extensible**: Easy to add new languages
- **Performant**: Minimal overhead
- **User-friendly**: Simple language switching

For more details, see:
- `LANGUAGE_SYSTEM.md` - Technical documentation
- `LANGUAGE_QUICKSTART.md` - Quick start guide
