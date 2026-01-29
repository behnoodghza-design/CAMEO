#!/usr/bin/env python3
"""
PDF-to-Database Mapper Agent

This script maps PDF files with cryptic filenames (e.g., ACT.pdf, AEL.pdf) 
to chemical records in the SQLite database by extracting CAS numbers from PDFs.

Usage:
    python scripts/map_pdfs.py --pdf-dir /path/to/pdfs --db /path/to/chemicals.db

Requirements:
    pip install PyMuPDF  # or: pip install pymupdf
"""

import argparse
import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

# Try to import PDF library
try:
    import fitz  # PyMuPDF
    PDF_LIBRARY = 'pymupdf'
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = 'pdfplumber'
    except ImportError:
        PDF_LIBRARY = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Regex patterns for CAS extraction
CAS_PATTERNS = [
    # Section 2.5 pattern from CAMEO datasheets
    r'2\.5\s+CAS\s+Registry\s+No\.?:?\s*([0-9]{2,7}-[0-9]{2}-[0-9])',
    # Generic CAS pattern with label
    r'CAS\s+(?:Registry\s+)?(?:No\.?|Number|#):?\s*([0-9]{2,7}-[0-9]{2}-[0-9])',
    # Standalone CAS number pattern (fallback)
    r'\b([0-9]{2,7}-[0-9]{2}-[0-9])\b',
]

# Pattern to extract chemical name from first page
NAME_PATTERN = r'^([A-Z][A-Z0-9,\-\(\)\s]{2,50})$'


def ensure_schema(db_path: str) -> None:
    """Add local_pdf_filename column if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(chemicals)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'local_pdf_filename' not in columns:
        logger.info("Adding 'local_pdf_filename' column to chemicals table...")
        cursor.execute("ALTER TABLE chemicals ADD COLUMN local_pdf_filename TEXT")
        conn.commit()
        logger.info("Column added successfully.")
    else:
        logger.info("Column 'local_pdf_filename' already exists.")
    
    conn.close()


def extract_text_from_pdf_pymupdf(pdf_path: str, max_pages: int = 3) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(min(max_pages, len(doc))):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
    except Exception as e:
        logger.error(f"Error reading {pdf_path} with PyMuPDF: {e}")
    return text


def extract_text_from_pdf_pdfplumber(pdf_path: str, max_pages: int = 3) -> str:
    """Extract text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading {pdf_path} with pdfplumber: {e}")
    return text


def extract_text_from_pdf(pdf_path: str, max_pages: int = 3) -> str:
    """Extract text from PDF using available library."""
    if PDF_LIBRARY == 'pymupdf':
        return extract_text_from_pdf_pymupdf(pdf_path, max_pages)
    elif PDF_LIBRARY == 'pdfplumber':
        return extract_text_from_pdf_pdfplumber(pdf_path, max_pages)
    else:
        logger.error("No PDF library available. Install PyMuPDF: pip install pymupdf")
        return ""


def extract_cas_from_text(text: str) -> Optional[str]:
    """Extract CAS number from text using multiple patterns."""
    for pattern in CAS_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            cas = match.group(1)
            # Validate CAS format
            if re.match(r'^[0-9]{2,7}-[0-9]{2}-[0-9]$', cas):
                return cas
    return None


def extract_chemical_name_from_text(text: str) -> Optional[str]:
    """Extract chemical name from first few lines of text."""
    lines = text.split('\n')[:10]
    for line in lines:
        line = line.strip()
        # Look for all-caps chemical names
        if re.match(r'^[A-Z][A-Z0-9,\-\(\)\s]{2,50}$', line):
            # Skip common headers
            if line not in ['CHEMICAL', 'DATASHEET', 'CAMEO', 'CHEMICALS']:
                return line
    return None


def find_chemical_by_cas(cursor: sqlite3.Cursor, cas: str) -> Optional[Tuple[int, str]]:
    """Find chemical in database by CAS number."""
    # Query the chemical_cas junction table
    cursor.execute("""
        SELECT c.id, c.name 
        FROM chemicals c
        JOIN chemical_cas cc ON c.id = cc.chem_id
        WHERE cc.cas_id = ?
    """, (cas,))
    row = cursor.fetchone()
    if row:
        return (row[0], row[1])
    return None


def find_chemical_by_chris_code(cursor: sqlite3.Cursor, chris_code: str) -> Optional[Tuple[int, str]]:
    """Find chemical in database by CHRIS code."""
    cursor.execute("""
        SELECT id, name 
        FROM chemicals 
        WHERE chris_codes LIKE ?
    """, (f'%{chris_code}%',))
    row = cursor.fetchone()
    if row:
        return (row[0], row[1])
    return None


def find_chemical_by_name(cursor: sqlite3.Cursor, name: str) -> Optional[Tuple[int, str]]:
    """Find chemical in database by name."""
    cursor.execute("""
        SELECT id, name 
        FROM chemicals 
        WHERE UPPER(name) = UPPER(?) OR UPPER(synonyms) LIKE UPPER(?)
    """, (name, f'%{name}%'))
    row = cursor.fetchone()
    if row:
        return (row[0], row[1])
    return None


def update_chemical_pdf_link(cursor: sqlite3.Cursor, chem_id: int, pdf_filename: str) -> None:
    """Update chemical record with PDF filename."""
    cursor.execute("""
        UPDATE chemicals 
        SET local_pdf_filename = ?
        WHERE id = ?
    """, (pdf_filename, chem_id))


def process_pdf(pdf_path: Path, cursor: sqlite3.Cursor, stats: dict) -> bool:
    """Process a single PDF file and attempt to map it to database."""
    filename = pdf_path.name
    chris_code = pdf_path.stem.upper()  # e.g., 'ACT' from 'ACT.pdf'
    
    logger.info(f"Processing: {filename}")
    
    # Strategy 1: Try CHRIS code first (fastest)
    result = find_chemical_by_chris_code(cursor, chris_code)
    if result:
        chem_id, chem_name = result
        update_chemical_pdf_link(cursor, chem_id, filename)
        logger.info(f"  ✓ Mapped via CHRIS code '{chris_code}' → {chem_name} (ID: {chem_id})")
        stats['mapped_chris'] += 1
        return True
    
    # Strategy 2: Extract text and find CAS
    text = extract_text_from_pdf(str(pdf_path))
    if not text:
        logger.warning(f"  ✗ Could not extract text from {filename}")
        stats['failed_extract'] += 1
        return False
    
    cas = extract_cas_from_text(text)
    if cas:
        result = find_chemical_by_cas(cursor, cas)
        if result:
            chem_id, chem_name = result
            update_chemical_pdf_link(cursor, chem_id, filename)
            logger.info(f"  ✓ Mapped via CAS '{cas}' → {chem_name} (ID: {chem_id})")
            stats['mapped_cas'] += 1
            return True
        else:
            logger.warning(f"  ✗ CAS '{cas}' found in PDF but no DB match")
            stats['no_db_match'] += 1
    
    # Strategy 3: Try chemical name from PDF
    chem_name_from_pdf = extract_chemical_name_from_text(text)
    if chem_name_from_pdf:
        result = find_chemical_by_name(cursor, chem_name_from_pdf)
        if result:
            chem_id, chem_name = result
            update_chemical_pdf_link(cursor, chem_id, filename)
            logger.info(f"  ✓ Mapped via name '{chem_name_from_pdf}' → {chem_name} (ID: {chem_id})")
            stats['mapped_name'] += 1
            return True
    
    logger.warning(f"  ✗ Could not map {filename} to any chemical")
    stats['unmapped'] += 1
    return False


def main():
    parser = argparse.ArgumentParser(description='Map PDF files to chemical database records')
    parser.add_argument('--pdf-dir', required=True, help='Directory containing PDF files')
    parser.add_argument('--db', required=True, help='Path to chemicals.db SQLite database')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify database')
    args = parser.parse_args()
    
    pdf_dir = Path(args.pdf_dir)
    db_path = args.db
    
    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return 1
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return 1
    
    if PDF_LIBRARY is None:
        logger.error("No PDF library available. Install PyMuPDF: pip install pymupdf")
        return 1
    
    logger.info(f"Using PDF library: {PDF_LIBRARY}")
    logger.info(f"PDF directory: {pdf_dir}")
    logger.info(f"Database: {db_path}")
    
    # Ensure schema has required column
    if not args.dry_run:
        ensure_schema(db_path)
    
    # Find all PDF files
    pdf_files = list(pdf_dir.glob('*.pdf'))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    if not pdf_files:
        logger.warning("No PDF files found in directory")
        return 0
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Process statistics
    stats = {
        'mapped_chris': 0,
        'mapped_cas': 0,
        'mapped_name': 0,
        'no_db_match': 0,
        'failed_extract': 0,
        'unmapped': 0,
    }
    
    # Process each PDF
    for pdf_path in sorted(pdf_files):
        process_pdf(pdf_path, cursor, stats)
    
    # Commit changes
    if not args.dry_run:
        conn.commit()
        logger.info("Changes committed to database")
    else:
        logger.info("Dry run - no changes made")
    
    conn.close()
    
    # Print summary
    total = len(pdf_files)
    mapped = stats['mapped_chris'] + stats['mapped_cas'] + stats['mapped_name']
    
    logger.info("\n" + "="*50)
    logger.info("MAPPING SUMMARY")
    logger.info("="*50)
    logger.info(f"Total PDFs processed: {total}")
    logger.info(f"Successfully mapped:  {mapped} ({100*mapped/total:.1f}%)")
    logger.info(f"  - Via CHRIS code:   {stats['mapped_chris']}")
    logger.info(f"  - Via CAS number:   {stats['mapped_cas']}")
    logger.info(f"  - Via name match:   {stats['mapped_name']}")
    logger.info(f"Failed to map:        {total - mapped}")
    logger.info(f"  - No DB match:      {stats['no_db_match']}")
    logger.info(f"  - Extract failed:   {stats['failed_extract']}")
    logger.info(f"  - Unmapped:         {stats['unmapped']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
