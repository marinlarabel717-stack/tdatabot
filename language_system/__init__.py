#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Language System Package for TDataBot
Non-intrusive multi-language support system
"""

from .language_manager import get_language_manager, translate
from .language_middleware import get_middleware, with_language
from .language_bootstrap import bootstrap_language_system, inject_language_system

__all__ = [
    'get_language_manager',
    'translate',
    'get_middleware',
    'with_language',
    'bootstrap_language_system',
    'inject_language_system',
]

__version__ = '1.0.0'
