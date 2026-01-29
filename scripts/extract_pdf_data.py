#!/usr/bin/env python3
"""
PDF Data Extraction Script - Gap Filling Only

Extracts regulatory and hazard information from linked PDFs
and fills ONLY empty/null fields in the database.

Does NOT overwrite existing data.
"""

import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)


class PDFExtractor:
    """Extract structured data from CAMEO PDF datasheets."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = self._extract_full_text()
    
    def _extract_full_text(self) -> str:
        """Extract all text from PDF."""
        try:
            doc = fitz.open(self.pdf_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"ERROR extracting text from {self.pdf_path}: {e}")
            return ""
    
    def extract_epa_rq(self) -> Optional[int]:
        """Extract EPA Reportable Quantity."""
        patterns = [
            r'EPA\s+Reportable\s+Quantity\s*:\s*(\d+)',
            r'Reportable\s+Quantity\s*:\s*(\d+)\s*(?:pounds?|lbs?)?',
            r'RQ\s*:\s*(\d+)\s*(?:pounds?|lbs?)?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def extract_rcra_code(self) -> Optional[str]:
        """Extract RCRA waste code."""
        patterns = [
            r'RCRA\s+Waste\s+Number\s*:\s*([A-Z]\d{3})',
            r'RCRA\s+(?:Waste\s+)?Code\s*:\s*([A-Z]\d{3})',
            r'RCRA\s*:\s*([A-Z]\d{3})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_dot_hazard_class(self) -> Optional[str]:
        """Extract DOT Hazard Class."""
        pattern = r'DOT\s+Hazard\s+Class\s*[:\(]?\s*([\d\.]+)'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def extract_physical_warnings(self) -> list:
        """Extract physical behavior warnings (floats, sinks, etc.)."""
        warnings = []
        
        # Float/sink patterns
        if re.search(r'floats?\s+on\s+water', self.text, re.IGNORECASE):
            warnings.append("Floats on water")
        elif re.search(r'sinks?\s+in\s+water', self.text, re.IGNORECASE):
            warnings.append("Sinks in water")
        
        # Vapor patterns
        if re.search(r'vapors?\s+heavier\s+than\s+air', self.text, re.IGNORECASE):
            warnings.append("Vapors heavier than air")
        elif re.search(r'vapors?\s+lighter\s+than\s+air', self.text, re.IGNORECASE):
            warnings.append("Vapors lighter than air")
        
        # Solubility
        if re.search(r'(?:slightly|sparingly)\s+soluble\s+in\s+water', self.text, re.IGNORECASE):
            warnings.append("Slightly soluble in water")
        elif re.search(r'insoluble\s+in\s+water', self.text, re.IGNORECASE):
            warnings.append("Insoluble in water")
        elif re.search(r'(?:very|highly)\s+soluble\s+in\s+water', self.text, re.IGNORECASE):
            warnings.append("Highly soluble in water")
        
        return warnings
    
    def extract_detailed_health_hazards(self) -> Optional[str]:
        """Extract detailed health hazards section."""
        # Look for "HEALTH HAZARD INFORMATION" section
        pattern = r'HEALTH\s+HAZARD\s+INFORMATION\s*[:\n]+(.*?)(?=\n\s*[A-Z\s]{10,}[:\n]|\Z)'
        match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Clean up and limit length
            text = re.sub(r'\s+', ' ', text)
            return text[:2000]  # Limit to 2000 chars
        return None
    
    def extract_detailed_fire_hazards(self) -> Optional[str]:
        """Extract detailed fire hazards section."""
        pattern = r'FIRE\s+HAZARD\s+INFORMATION\s*[:\n]+(.*?)(?=\n\s*[A-Z\s]{10,}[:\n]|\Z)'
        match = re.search(pattern, self.text, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            text = re.sub(r'\s+', ' ', text)
            return text[:2000]
        return None
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all available data."""
        return {
            'epa_rq': self.extract_epa_rq(),
            'rcra_code': self.extract_rcra_code(),
            'dot_hazard_class': self.extract_dot_hazard_class(),
            'physical_warnings': self.extract_physical_warnings(),
            'health_hazards_detailed': self.extract_detailed_health_hazards(),
            'fire_hazards_detailed': self.extract_detailed_fire_hazards(),
        }


def ensure_regulatory_columns(db_path: str) -> None:
    """Add regulatory columns if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(chemicals)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    new_columns = {
        'epa_rq': 'INTEGER',
        'rcra_code': 'TEXT',
        'dot_hazard_class': 'TEXT',
        'physical_warnings': 'TEXT',
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in existing_cols:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE chemicals ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    conn.close()


def should_update_field(current_value: Any) -> bool:
    """Check if field should be updated (only if null/empty)."""
    if current_value is None:
        return True
    if isinstance(current_value, str) and not current_value.strip():
        return True
    return False


def process_chemical(chem_id: int, chem_name: str, pdf_path: Path, cursor: sqlite3.Cursor) -> Dict[str, int]:
    """Process a single chemical and update database."""
    stats = {
        'epa_rq': 0,
        'rcra_code': 0,
        'dot_hazard_class': 0,
        'physical_warnings': 0,
        'health_haz': 0,
        'fire_haz': 0,
    }
    
    if not pdf_path.exists():
        return stats
    
    # Get current values
    cursor.execute("""
        SELECT epa_rq, rcra_code, dot_hazard_class, physical_warnings, 
               health_haz, fire_haz, description
        FROM chemicals 
        WHERE id = ?
    """, (chem_id,))
    
    row = cursor.fetchone()
    if not row:
        return stats
    
    current = {
        'epa_rq': row[0],
        'rcra_code': row[1],
        'dot_hazard_class': row[2],
        'physical_warnings': row[3],
        'health_haz': row[4],
        'fire_haz': row[5],
        'description': row[6],
    }
    
    # Extract data from PDF
    extractor = PDFExtractor(str(pdf_path))
    extracted = extractor.extract_all()
    
    updates = {}
    
    # EPA RQ
    if should_update_field(current['epa_rq']) and extracted['epa_rq']:
        updates['epa_rq'] = extracted['epa_rq']
        stats['epa_rq'] = 1
    
    # RCRA Code
    if should_update_field(current['rcra_code']) and extracted['rcra_code']:
        updates['rcra_code'] = extracted['rcra_code']
        stats['rcra_code'] = 1
    
    # DOT Hazard Class
    if should_update_field(current['dot_hazard_class']) and extracted['dot_hazard_class']:
        updates['dot_hazard_class'] = extracted['dot_hazard_class']
        stats['dot_hazard_class'] = 1
    
    # Physical Warnings
    if extracted['physical_warnings']:
        warnings_text = "; ".join(extracted['physical_warnings'])
        if should_update_field(current['physical_warnings']):
            updates['physical_warnings'] = warnings_text
            stats['physical_warnings'] = 1
        elif current['description'] and warnings_text not in current['description']:
            # Append to description if not already there
            new_desc = current['description'] + f" {warnings_text}"
            updates['description'] = new_desc
    
    # Health Hazards (only if current is short/empty)
    if extracted['health_hazards_detailed']:
        if should_update_field(current['health_haz']) or (
            current['health_haz'] and len(current['health_haz']) < 200
        ):
            updates['health_haz'] = extracted['health_hazards_detailed']
            stats['health_haz'] = 1
    
    # Fire Hazards (only if current is short/empty)
    if extracted['fire_hazards_detailed']:
        if should_update_field(current['fire_haz']) or (
            current['fire_haz'] and len(current['fire_haz']) < 200
        ):
            updates['fire_haz'] = extracted['fire_hazards_detailed']
            stats['fire_haz'] = 1
    
    # Apply updates
    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [chem_id]
        cursor.execute(f"UPDATE chemicals SET {set_clause} WHERE id = ?", values)
        print(f"  ✓ Updated {chem_name}: {', '.join(updates.keys())}")
    
    return stats


def main():
    db_path = "resources/chemicals.db"
    pdf_base_dir = Path(r"C:\Users\aminh\OneDrive\Desktop\CAMEO\PDF_Folder\Material")
    
    if not pdf_base_dir.exists():
        print(f"ERROR: PDF directory not found: {pdf_base_dir}")
        return 1
    
    print("Ensuring database schema...")
    ensure_regulatory_columns(db_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all chemicals with linked PDFs
    cursor.execute("""
        SELECT id, name, local_pdf_filename 
        FROM chemicals 
        WHERE local_pdf_filename IS NOT NULL
        ORDER BY id
    """)
    
    chemicals = cursor.fetchall()
    
    if not chemicals:
        print("ERROR: No chemicals with linked PDFs found")
        return 1
    
    print(f"Found {len(chemicals)} chemicals with linked PDFs")
    print("Starting gap-filling extraction...\n")
    
    # Global stats
    total_stats = {
        'epa_rq': 0,
        'rcra_code': 0,
        'dot_hazard_class': 0,
        'physical_warnings': 0,
        'health_haz': 0,
        'fire_haz': 0,
    }
    
    processed = 0
    
    for chem_id, chem_name, pdf_filename in chemicals:
        pdf_path = pdf_base_dir / pdf_filename
        
        if processed % 100 == 0:
            print(f"Progress: {processed}/{len(chemicals)}")
        
        stats = process_chemical(chem_id, chem_name, pdf_path, cursor)
        
        for key in total_stats:
            total_stats[key] += stats[key]
        
        processed += 1
        
        # Commit every 50 records
        if processed % 50 == 0:
            conn.commit()
    
    # Final commit
    conn.commit()
    conn.close()
    
    # Print summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    print(f"Chemicals processed:     {processed}")
    print(f"EPA RQ extracted:        {total_stats['epa_rq']}")
    print(f"RCRA codes extracted:    {total_stats['rcra_code']}")
    print(f"DOT classes extracted:   {total_stats['dot_hazard_class']}")
    print(f"Physical warnings added: {total_stats['physical_warnings']}")
    print(f"Health hazards updated:  {total_stats['health_haz']}")
    print(f"Fire hazards updated:    {total_stats['fire_haz']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
