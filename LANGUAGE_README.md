# Language System Quick Reference

The language switching system files have been organized into the `language_system/` directory for better maintainability.

## Starting the Bot with Language Support

```bash
# From the root directory
python language_system/start_with_language.py

# Or navigate to the language_system directory first
cd language_system
python start_with_language.py
```

## Directory Structure

```
language_system/
├── README.md                   # Main documentation
├── __init__.py                # Package initialization
├── start_with_language.py     # Bot launcher script
├── language_manager.py        # Core translation engine
├── language_middleware.py     # User preferences
├── language_integration.py    # Menu handlers
├── menu_wrapper.py           # Menu patching
├── language_bootstrap.py     # System initialization
├── lang/                     # Translation files
│   ├── en.json              # English
│   ├── zh.json              # Chinese
│   └── ru.json              # Russian
├── docs/                     # Documentation
│   ├── LANGUAGE_QUICKSTART.md
│   ├── LANGUAGE_SYSTEM.md
│   ├── LANGUAGE_DEMO.md
│   └── IMPLEMENTATION_COMPLETE.md
└── tests/                    # Test files
    ├── test_language_core.py
    └── test_language_system.py
```

## Testing

```bash
# Run core tests
cd language_system/tests
python test_language_core.py
```

## Documentation

- [README](language_system/README.md) - Overview and quick start
- [Quick Start Guide](language_system/docs/LANGUAGE_QUICKSTART.md) - User guide
- [Technical Docs](language_system/docs/LANGUAGE_SYSTEM.md) - Architecture details
- [Demo](language_system/docs/LANGUAGE_DEMO.md) - Visual examples

## Features

- 🌐 Multi-language support (English, Chinese, Russian)
- 💾 Persistent user preferences
- 🔄 Non-blocking UI updates
- 📦 100% non-intrusive design (no modifications to tdata.py)
- ✨ Easy to extend with new languages

## Adding a New Language

1. Create a new JSON file: `language_system/lang/your_code.json`
2. Copy the structure from `en.json` and translate
3. Add language name in `language_manager.py`
4. Restart the bot

For detailed instructions, see [LANGUAGE_QUICKSTART.md](language_system/docs/LANGUAGE_QUICKSTART.md).
