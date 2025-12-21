# Language Switch System for TDataBot

## Overview

This is a **non-intrusive** language switching system that adds multi-language support to TDataBot without modifying the original `tdata.py` or other core files.

## Features

- 🌐 **Multi-language Support**: Easily add new languages via JSON files
- 🔄 **Automatic Fallback**: Falls back to default language if translation is missing
- 💾 **User Preferences**: Stores each user's language preference in the database
- 🎯 **Non-intrusive Design**: No modifications to existing code
- 🚀 **Dynamic Integration**: Uses decorators and wrappers to inject functionality

## Architecture

### Components

1. **language_manager.py** - Core translation management
   - Loads and manages translation files from `lang/` directory
   - Provides translation lookup with fallback support
   - Supports nested keys (e.g., `menu.welcome`)

2. **language_middleware.py** - User language preferences
   - Stores user language preferences in SQLite database
   - Provides context for translations
   - Decorator support for handlers

3. **language_integration.py** - Handler registration
   - Registers callback handlers for language switching
   - Manages language selection menu
   - Handles language change requests

4. **menu_wrapper.py** - Dynamic menu extension
   - Wraps the main menu to add language selection button
   - Non-intrusive patching using Python's dynamic features

5. **language_bootstrap.py** - System initialization
   - Bootstraps the entire language system
   - Patches the bot during initialization
   - Auto-injects when imported

## Usage

### Starting the Bot with Language Support

**Option 1: Use the launcher script (Recommended)**

```bash
python start_with_language.py
```

**Option 2: Modify your startup to import the bootstrap**

```python
import language_bootstrap  # Import before starting bot
import tdata
tdata.main()
```

### Adding New Languages

1. Create a new JSON file in the `lang/` directory:
   ```
   lang/es.json  # Spanish
   lang/fr.json  # French
   ```

2. Follow the structure of existing language files:
   ```json
   {
     "menu": {
       "welcome": "Your translation here",
       "select_language": "🌐 Seleccionar idioma"
     },
     "language": {
       "changed": "✅ Idioma cambiado",
       "current": "Idioma actual"
     }
   }
   ```

3. The language will be automatically detected and added to the selection menu.

### Supported Languages

Currently supported languages:
- 🇬🇧 English (en)
- 🇨🇳 Chinese (zh)

## How It Works

### 1. Translation Lookup

```python
from language_manager import translate

# Get translation with automatic fallback
text = translate('menu.welcome', lang='zh')
```

### 2. User Preferences

```python
from language_middleware import get_middleware

middleware = get_middleware()

# Get user's language
lang = middleware.get_user_language(user_id)

# Set user's language
middleware.set_user_language(user_id, 'zh')

# Translate for specific user
text = middleware.translate_for_user(user_id, 'menu.welcome')
```

### 3. Menu Integration

The system automatically:
1. Adds a "🌐 Select Language" button to the main menu
2. Shows available languages when clicked
3. Updates user preference when language is selected
4. Refreshes the menu in the new language

## Database Schema

The system creates a `user_language` table:

```sql
CREATE TABLE user_language (
    user_id INTEGER PRIMARY KEY,
    language_code TEXT NOT NULL DEFAULT 'en',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Translation Key Structure

```json
{
  "menu": {
    "welcome": "Welcome message",
    "select_language": "Language selection prompt",
    "account_check": "Account check button",
    ...
  },
  "language": {
    "changed": "Language changed confirmation",
    "current": "Current language display",
    "select_prompt": "Selection prompt"
  },
  "status": {
    "version": "Version label",
    ...
  },
  "common": {
    "yes": "Yes",
    "no": "No",
    ...
  }
}
```

## Extension Points

### Adding New Translations

To translate a new UI element:

1. Add the key to all language files:
   ```json
   {
     "new_feature": {
       "button_text": "Your translation"
     }
   }
   ```

2. Use in your code:
   ```python
   text = middleware.translate_for_user(user_id, 'new_feature.button_text')
   ```

### Custom Language Names

Edit `language_manager.py` to add more language names:

```python
def get_language_name(self, lang_code: str) -> str:
    names = {
        'en': 'English',
        'zh': '中文',
        'es': 'Español',  # Add new languages here
        'fr': 'Français',
    }
    return names.get(lang_code, lang_code.upper())
```

## Testing

### Manual Testing

1. Start the bot with language support
2. Send `/start` command
3. Look for the "🌐 Select Language" button in the main menu
4. Click it and select a different language
5. Verify that the menu updates with translations

### Adding Translations for Testing

You can test by adding a simple language file:

```json
{
  "menu": {
    "welcome": "TEST: Welcome message"
  }
}
```

## Troubleshooting

### Language button not appearing

- Check that `language_bootstrap.py` is imported before the bot starts
- Verify the bot's `main_menu` method exists and is being called

### Translations not loading

- Check that JSON files are valid
- Verify the `lang/` directory exists
- Check logs for loading errors

### Database errors

- Ensure write permissions for the database file
- Check that the `user_language` table was created

## Technical Notes

### Non-intrusive Design

The system uses several Python techniques to avoid modifying existing code:

1. **Method Wrapping**: Wraps the `main_menu` method using decorators
2. **Dynamic Patching**: Patches the bot's `__init__` method at runtime
3. **Handler Registration**: Adds new callback handlers via the dispatcher
4. **Middleware Pattern**: Intercepts and enhances existing functionality

### Performance Considerations

- Translation files are loaded once at startup
- User language preferences are cached where possible
- Database queries are minimal (one per language change)

## Future Enhancements

Possible improvements:
- [ ] Add more languages
- [ ] Translate all UI elements (currently only menu)
- [ ] Add language auto-detection based on Telegram settings
- [ ] Cache translations in memory for better performance
- [ ] Add translation validation tool
- [ ] Support for pluralization rules
- [ ] RTL language support

## License

This language system follows the same license as the main TDataBot project.
