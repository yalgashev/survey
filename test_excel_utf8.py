#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test UTF-8 encoding in Excel export"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from openpyxl import Workbook

# Create a test workbook
wb = Workbook()
ws = wb.active
ws.title = "UTF-8 Test"

# Test data with various languages
test_data = [
    ['#', 'Language', 'Text'],
    [1, 'English', 'The best tutor ever'],
    [2, 'Russian', 'Прекрасный преподаватель, объясняет очень понятно'],
    [3, 'Chinese', '这位老师非常好'],
    [4, 'Uzbek', "O'qituvchi juda yaxshi tushuntiradi"],
    [5, 'Mixed', 'Отличный teacher 非常好'],
]

for row in test_data:
    # Ensure all values are properly encoded strings
    encoded_row = [str(cell) if cell is not None else '' for cell in row]
    ws.append(encoded_row)

# Save to file
output_file = 'utf8_test.xlsx'
wb.save(output_file)

print(f"✓ Test Excel file created: {output_file}")
print("✓ Contains text in multiple languages (English, Russian, Chinese, Uzbek)")
print("✓ Please open the file to verify all characters display correctly")
