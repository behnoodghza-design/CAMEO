#!/usr/bin/env python3
"""
PDF Mapping Audit Script

Randomly selects 5 chemicals with linked PDFs and verifies the mapping
by comparing database names with PDF content.
"""

import random
import sqlite3
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)


def extract_first_lines(pdf_path: str, num_lines: int = 5) -> list:
    """Extract first N lines from PDF."""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return []
        
        page = doc[0]
        text = page.get_text()
        doc.close()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines[:num_lines]
    except Exception as e:
        return [f"ERROR: {e}"]


def fuzzy_match(db_name: str, pdf_lines: list) -> bool:
    """Check if database name appears in PDF lines (fuzzy)."""
    db_upper = db_name.upper()
    
    for line in pdf_lines:
        line_upper = line.upper()
        # Check if DB name is in line or line is in DB name
        if db_upper in line_upper or line_upper in db_upper:
            return True
        
        # Check word overlap (at least 50% of words match)
        db_words = set(db_upper.split())
        line_words = set(line_upper.split())
        if db_words and line_words:
            overlap = len(db_words & line_words) / len(db_words)
            if overlap >= 0.5:
                return True
    
    return False


def main():
    db_path = "resources/chemicals.db"
    pdf_base_dir = Path(r"C:\Users\aminh\OneDrive\Desktop\CAMEO\PDF_Folder\Material")
    
    if not pdf_base_dir.exists():
        print(f"ERROR: PDF directory not found: {pdf_base_dir}")
        return 1
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all chemicals with linked PDFs
    cursor.execute("""
        SELECT id, name, local_pdf_filename 
        FROM chemicals 
        WHERE local_pdf_filename IS NOT NULL
    """)
    
    all_mapped = cursor.fetchall()
    
    if not all_mapped:
        print("ERROR: No chemicals with linked PDFs found in database")
        return 1
    
    print(f"Found {len(all_mapped)} chemicals with linked PDFs")
    print("Selecting 5 random samples for audit...\n")
    print("="*70)
    
    # Select 5 random samples
    samples = random.sample(all_mapped, min(5, len(all_mapped)))
    
    match_count = 0
    mismatch_count = 0
    
    for i, row in enumerate(samples, 1):
        chem_id = row['id']
        db_name = row['name']
        pdf_filename = row['local_pdf_filename']
        pdf_path = pdf_base_dir / pdf_filename
        
        print(f"\n{i}. AUDIT SAMPLE #{i}")
        print(f"   Database ID:   {chem_id}")
        print(f"   Database Name: {db_name}")
        print(f"   Linked PDF:    {pdf_filename}")
        
        if not pdf_path.exists():
            print(f"   ❌ ERROR: PDF file not found at {pdf_path}")
            mismatch_count += 1
            continue
        
        # Extract first lines from PDF
        pdf_lines = extract_first_lines(str(pdf_path), num_lines=5)
        
        print(f"   PDF First Lines:")
        for j, line in enumerate(pdf_lines[:3], 1):
            print(f"      {j}. {line[:80]}")  # Truncate long lines
        
        # Check match
        is_match = fuzzy_match(db_name, pdf_lines)
        
        if is_match:
            print(f"   ✅ MATCH - Names align correctly")
            match_count += 1
        else:
            print(f"   ❌ MISMATCH - Names do not match!")
            mismatch_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("AUDIT SUMMARY")
    print("="*70)
    print(f"Samples audited:  {len(samples)}")
    print(f"Matches:          {match_count} ✅")
    print(f"Mismatches:       {mismatch_count} ❌")
    
    if mismatch_count == 0:
        print("\n✅ ALL SAMPLES PASSED - Mapping appears correct!")
        return 0
    else:
        print(f"\n⚠️  {mismatch_count} mismatches detected - Review mapping logic")
        return 1


if __name__ == '__main__':
    sys.exit(main())
