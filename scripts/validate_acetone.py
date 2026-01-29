#!/usr/bin/env python3
"""
Validate ACETONE record - Step 4 verification
"""

import sqlite3

def main():
    db_path = "resources/chemicals.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find ACETONE
    cursor.execute("""
        SELECT c.id, c.name, c.chris_codes, c.epa_rq, c.physical_warnings,
               cc.cas_id
        FROM chemicals c
        LEFT JOIN chemical_cas cc ON c.id = cc.chem_id
        WHERE UPPER(c.name) LIKE '%ACETONE%'
        ORDER BY c.id
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    
    print("="*70)
    print("ACETONE VALIDATION RESULTS")
    print("="*70)
    
    for row in results:
        print(f"\nChemical ID:      {row['id']}")
        print(f"Name:             {row['name']}")
        print(f"CAS Number:       {row['cas_id']}")
        print(f"CHRIS Code:       {row['chris_codes']}")
        print(f"EPA RQ:           {row['epa_rq']}")
        print(f"Physical Warnings: {row['physical_warnings']}")
        
        # Check if ACT.pdf is linked
        cursor.execute("SELECT local_pdf_filename FROM chemicals WHERE id = ?", (row['id'],))
        pdf_row = cursor.fetchone()
        if pdf_row:
            print(f"Linked PDF:       {pdf_row['local_pdf_filename']}")
        else:
            print(f"Linked PDF:       (column not found)")
    
    # Check if local_pdf_filename column exists
    cursor.execute("PRAGMA table_info(chemicals)")
    columns = [r[1] for r in cursor.fetchall()]
    
    print("\n" + "="*70)
    print("SCHEMA CHECK")
    print("="*70)
    print(f"local_pdf_filename column exists: {'local_pdf_filename' in columns}")
    print(f"epa_rq column exists: {'epa_rq' in columns}")
    print(f"rcra_code column exists: {'rcra_code' in columns}")
    print(f"physical_warnings column exists: {'physical_warnings' in columns}")
    
    # Count mapped PDFs
    if 'local_pdf_filename' in columns:
        cursor.execute("SELECT COUNT(*) FROM chemicals WHERE local_pdf_filename IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"\nTotal chemicals with linked PDFs: {count}")
    
    # Count EPA RQ values
    if 'epa_rq' in columns:
        cursor.execute("SELECT COUNT(*) FROM chemicals WHERE epa_rq IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"Total chemicals with EPA RQ: {count}")
    
    conn.close()
    
    return 0


if __name__ == '__main__':
    exit(main())
