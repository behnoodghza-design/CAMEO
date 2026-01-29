#!/usr/bin/env python3
"""
Debug ACETONE PDF extraction
"""

import re
from pathlib import Path

try:
    import fitz
except ImportError:
    print("ERROR: PyMuPDF not installed")
    exit(1)

pdf_path = Path(r"C:\Users\aminh\OneDrive\Desktop\CAMEO\PDF_Folder\Material\ACT.pdf")

if not pdf_path.exists():
    print(f"ERROR: PDF not found at {pdf_path}")
    exit(1)

print("Extracting text from ACT.pdf...")
doc = fitz.open(str(pdf_path))
full_text = ""
for page in doc:
    full_text += page.get_text() + "\n"
doc.close()

print(f"Total text length: {len(full_text)} characters\n")

# Search for EPA patterns
print("="*70)
print("SEARCHING FOR EPA REPORTABLE QUANTITY")
print("="*70)

# Show lines containing "EPA" or "Reportable"
lines = full_text.split('\n')
for i, line in enumerate(lines):
    if 'EPA' in line.upper() or 'REPORTABLE' in line.upper():
        print(f"Line {i}: {line.strip()}")

print("\n" + "="*70)
print("REGEX PATTERN TESTS")
print("="*70)

patterns = [
    r'EPA\s+Reportable\s+Quantity\s*[:\(]?\s*(\d+)\s*(?:pounds?|lbs?)',
    r'Reportable\s+Quantity\s*[:\(]?\s*(\d+)\s*(?:pounds?|lbs?)',
    r'RQ\s*[:\(]?\s*(\d+)\s*(?:pounds?|lbs?)',
    r'EPA.*?(\d+)\s*(?:pounds?|lbs?)',
]

for pattern in patterns:
    match = re.search(pattern, full_text, re.IGNORECASE)
    if match:
        print(f"✓ Pattern matched: {pattern}")
        print(f"  Captured: {match.group(1)}")
    else:
        print(f"✗ No match: {pattern}")

# Show section around "5000" if it exists
print("\n" + "="*70)
print("CONTEXT AROUND '5000'")
print("="*70)

if '5000' in full_text:
    idx = full_text.index('5000')
    context = full_text[max(0, idx-200):idx+200]
    print(context)
else:
    print("'5000' not found in PDF")
