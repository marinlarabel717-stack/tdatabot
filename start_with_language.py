#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDataBot Launcher with Language Support
This script initializes the language system before starting the bot
"""

import sys
import os

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🌐 ===== TDataBot with Language Support =====")
print("🌐 Initializing language system...")

# Import and inject language system BEFORE importing the main bot
try:
    import language_bootstrap
    print("✅ Language system loaded")
except Exception as e:
    print(f"⚠️ Warning: Language system failed to load: {e}")
    print("⚠️ Bot will continue without language support")

# Now import and run the main bot
print("🚀 Starting bot...")
import tdata

if __name__ == "__main__":
    tdata.main()
