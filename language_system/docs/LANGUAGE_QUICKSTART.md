# Quick Start Guide: Language System

## For Users

### Starting the Bot with Language Support

Simply run:

```bash
python start_with_language.py
```

This will:
1. Load the language system
2. Start the bot with language support enabled
3. Add a "🌐 Select Language" button to the main menu

### Switching Languages

1. Open the bot in Telegram
2. Click the "🌐 Select Language" button in the main menu
3. Select your preferred language from the list
4. The menu will refresh in your chosen language

### Supported Languages

- 🇬🇧 English (en)
- 🇨🇳 Chinese / 中文 (zh)

More languages can be added easily by creating new JSON files.

## For Developers

### Adding a New Language

1. Create a new JSON file: `lang/your_language.json`

Example for Spanish (`lang/es.json`):

```json
{
  "menu": {
    "welcome": "🤖 Bienvenido al Bot de Detección de Cuentas de Telegram",
    "select_language": "🌐 Seleccionar idioma",
    "account_check": "🚀 Verificación de cuenta",
    ...
  },
  "language": {
    "changed": "✅ Idioma cambiado a Español",
    "current": "Idioma actual: Español"
  },
  ...
}
```

2. Add the language name to `language_manager.py`:

```python
def get_language_name(self, lang_code: str) -> str:
    names = {
        'en': 'English',
        'zh': '中文',
        'es': 'Español',  # Add here
    }
    return names.get(lang_code, lang_code.upper())
```

3. Restart the bot - the new language will appear automatically!

### Translating Additional Text

To translate new UI elements:

1. Add the key to all language files:

```json
{
  "your_feature": {
    "button_text": "Your translation here"
  }
}
```

2. Use in code:

```python
from language_middleware import get_middleware

middleware = get_middleware()
text = middleware.translate_for_user(user_id, 'your_feature.button_text')
```

### Testing

Run the test suite:

```bash
python test_language_core.py
```

This verifies:
- Translation files are valid
- Database operations work
- All required keys are present
- Concurrent access is handled correctly

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│          start_with_language.py             │
│  (Entry point with language bootstrap)      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         language_bootstrap.py               │
│  (Initializes and patches the bot)          │
└──┬────────────┬─────────────┬───────────┬───┘
   │            │             │           │
   ▼            ▼             ▼           ▼
┌──────┐  ┌──────────┐  ┌────────┐  ┌────────┐
│ Lang │  │ Middle-  │  │ Integr │  │ Menu   │
│ Mgr  │  │ ware     │  │ ation  │  │ Wrap   │
└──────┘  └──────────┘  └────────┘  └────────┘
   │            │             │           │
   ▼            ▼             ▼           ▼
   JSON      Database     Handlers     Main Menu
   Files                               Extension
```

### Key Files

- `language_manager.py` - Loads and manages translations
- `language_middleware.py` - Stores user preferences
- `language_integration.py` - Handles language switching
- `menu_wrapper.py` - Adds language button to menu
- `language_bootstrap.py` - Initializes everything
- `lang/*.json` - Translation files

### Non-Intrusive Design

The system:
- ✅ Does NOT modify `tdata.py` or other core files
- ✅ Uses Python's dynamic features to patch at runtime
- ✅ Can be enabled/disabled easily
- ✅ Adds no overhead when not in use

### Troubleshooting

**Problem**: Language button not showing
- **Solution**: Make sure to use `start_with_language.py` instead of `tdata.py`

**Problem**: Translations not working
- **Solution**: Check that JSON files are valid using `python test_language_core.py`

**Problem**: Database errors
- **Solution**: Ensure write permissions for `bot_data.db`

**Problem**: Bot starts but language system doesn't load
- **Solution**: Check logs for import errors

## Examples

### Basic Usage

```python
from language_middleware import get_middleware

middleware = get_middleware()

# Get user's current language
user_lang = middleware.get_user_language(user_id)

# Translate something for a user
text = middleware.translate_for_user(user_id, 'menu.welcome')

# Change user's language
middleware.set_user_language(user_id, 'zh')
```

### In a Handler

```python
from language_middleware import with_language

@with_language
def my_handler(update, context):
    # Translation function is automatically injected
    t = context.user_data.get('translate')
    
    if t:
        welcome = t('menu.welcome')
        update.message.reply_text(welcome)
```

### Manual Translation

```python
from language_manager import translate

# Direct translation
text_en = translate('menu.welcome', lang='en')
text_zh = translate('menu.welcome', lang='zh')

# With format variables
greeting = translate('greeting.hello', lang='en', name='John')
```

## Support

For issues or questions:
1. Check `LANGUAGE_SYSTEM.md` for detailed documentation
2. Run `python test_language_core.py` to verify setup
3. Check logs for error messages

## Credits

Language system developed for TDataBot with a non-intrusive design approach.
