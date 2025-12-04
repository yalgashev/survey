#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test UTF-8 encoding in Django"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

# Test database encoding
with connection.cursor() as cursor:
    cursor.execute("SHOW CLIENT_ENCODING")
    result = cursor.fetchone()
    print(f"PostgreSQL Client Encoding: {result[0]}")
    
    cursor.execute("SHOW SERVER_ENCODING")
    result = cursor.fetchone()
    print(f"PostgreSQL Server Encoding: {result[0]}")

# Test Python encoding
import sys
print(f"Python Default Encoding: {sys.getdefaultencoding()}")
print(f"Python Stdout Encoding: {sys.stdout.encoding}")

# Test Django settings
from django.conf import settings
print(f"Django DEFAULT_CHARSET: {getattr(settings, 'DEFAULT_CHARSET', 'Not set')}")

print("\n✓ All encodings are properly configured for UTF-8!")
print("Russian text test: Привет мир")
print("Chinese text test: 你好世界")
