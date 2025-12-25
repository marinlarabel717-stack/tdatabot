# Language System for TDataBot

Non-intrusive multi-language support system that allows users to switch languages from the main menu.

## Directory Structure

```
language_system/
├── __init__.py                 # Package initialization
├── language_manager.py         # Translation management
├── language_middleware.py      # User preference storage
├── language_integration.py     # Callback handlers
├── menu_wrapper.py            # Menu patching
├── language_bootstrap.py      # System initialization
├── start_with_language.py     # Launcher script
├── lang/                      # Translation files
│   ├── en.json               # English
│   ├── zh.json               # Chinese
│   └── ru.json               # Russian
├── docs/                      # Documentation
│   ├── LANGUAGE_SYSTEM.md
│   ├── LANGUAGE_QUICKSTART.md
│   ├── LANGUAGE_DEMO.md
│   └── IMPLEMENTATION_COMPLETE.md
└── tests/                     # Test files
    ├── test_language_core.py
    └── test_language_system.py
```

## Quick Start

**The language system is now automatically integrated!** Simply start the bot normally:

```bash
# Start the bot directly - language system loads automatically
python tdata.py
```

The language system will automatically initialize when `tdata.py` starts.

**Alternative (Manual Launch):**
```bash
# You can still use the standalone launcher if needed
python language_system/start_with_language.py
```

## Documentation

- [Quick Start Guide](docs/LANGUAGE_QUICKSTART.md)
- [Technical Documentation](docs/LANGUAGE_SYSTEM.md)
- [Visual Demo](docs/LANGUAGE_DEMO.md)
- [Implementation Details](docs/IMPLEMENTATION_COMPLETE.md)

## Testing

```bash
# Run tests
cd language_system/tests
python test_language_core.py
```

## Features

- 🌐 Multi-language support (English, Chinese, Russian)
- 💾 Persistent user preferences
- 🔄 Non-blocking UI updates
- 📦 Automatic integration with tdata.py
- ✨ Easy to extend with new languages
