#!/usr/bin/env python3
"""
Re-extract ACETONE data with fixed regex patterns
"""

import sys
import sqlite3
from pathlib import Path

# Import the extractor
sys.path.insert(0, 'scripts')
from extract_pdf_data import PDFExtractor

def main():
    pdf_path = Path(r"C:\Users\aminh\OneDrive\Desktop\CAMEO\PDF_Folder\Material\ACT.pdf")
    db_path = "resources/chemicals.db"
    
    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return 1
    
    print("Extracting data from ACT.pdf with fixed patterns...")
    extractor = PDFExtractor(str(pdf_path))
    data = extractor.extract_all()
    
    print("\n" + "="*70)
    print("EXTRACTED DATA")
    print("="*70)
    print(f"EPA RQ:           {data['epa_rq']}")
    print(f"RCRA Code:        {data['rcra_code']}")
    print(f"DOT Hazard Class: {data['dot_hazard_class']}")
    print(f"Physical Warnings: {data['physical_warnings']}")
    
    # Update database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE chemicals 
        SET epa_rq = ?, rcra_code = ?
        WHERE name = 'ACETONE'
    """, (data['epa_rq'], data['rcra_code']))
    
    conn.commit()
    
    print("\n✓ Database updated for ACETONE")
    
    # Verify
    cursor.execute("SELECT id, name, epa_rq, rcra_code FROM chemicals WHERE name = 'ACETONE'")
    row = cursor.fetchone()
    
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"Chemical ID:  {row[0]}")
    print(f"Name:         {row[1]}")
    print(f"EPA RQ:       {row[2]}")
    print(f"RCRA Code:    {row[3]}")
    
    conn.close()
    
    if row[2] == 5000:
        print("\n✅ SUCCESS: EPA RQ correctly extracted (5000)")
        return 0
    else:
        print(f"\n❌ FAILED: EPA RQ is {row[2]}, expected 5000")
        return 1


if __name__ == '__main__':
    sys.exit(main())
