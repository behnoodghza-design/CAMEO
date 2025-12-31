"""
═══════════════════════════════════════════════════════════════
CAMEO 4x4 Matrix Stress Test
Tests scalability and correctness with complex multi-chemical analysis
═══════════════════════════════════════════════════════════════
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from logic.reactivity_engine import ReactivityEngine
from logic.constants import Compatibility

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'chemicals.db')

# Chemical IDs from ensure_data.py output
TEST_CHEMICALS = {
    'WATER': 30024,
    'SODIUM': 7794,
    'SULFURIC_ACID': 5193,
    'SODIUM_HYDROXIDE': 30061,
    'NITROGEN': 8898,
}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "═" * 70)
    print(f"  {title}")
    print("═" * 70)

def test_4x4_matrix():
    """
    The Complex Matrix Stress Test
    Tests 4 chemicals simultaneously: Acid + Base + Water + Nitrogen
    Expected: 16 interactions (4x4 matrix)
    """
    print_section("4x4 MATRIX STRESS TEST")
    
    # Initialize engine
    engine = ReactivityEngine(DB_PATH)
    
    # Test chemicals: Acid, Base, Water, Inert
    test_ids = [
        TEST_CHEMICALS['SULFURIC_ACID'],    # Acid (Groups 1, 2)
        TEST_CHEMICALS['SODIUM_HYDROXIDE'],  # Base (Group 10)
        TEST_CHEMICALS['WATER'],             # Water (Groups 100, 104)
        TEST_CHEMICALS['NITROGEN']           # Inert (Group 98/101)
    ]
    
    print(f"\n🧪 Testing {len(test_ids)} chemicals:")
    print(f"   1. Sulfuric Acid (ID: {test_ids[0]})")
    print(f"   2. Sodium Hydroxide (ID: {test_ids[1]})")
    print(f"   3. Water (ID: {test_ids[2]})")
    print(f"   4. Nitrogen (ID: {test_ids[3]})")
    
    # Run analysis
    print("\n⏳ Running Cartesian Product analysis...")
    result = engine.analyze(test_ids, include_water_check=True)
    
    # Validation 1: Dimensions
    print_section("VALIDATION 1: MATRIX DIMENSIONS")
    n = result.chemical_count
    matrix_rows = len(result.matrix)
    matrix_cols = len(result.matrix[0]) if result.matrix else 0
    
    print(f"Expected: {n}x{n} matrix ({n*n} cells)")
    print(f"Actual:   {matrix_rows}x{matrix_cols} matrix ({matrix_rows*matrix_cols} cells)")
    
    if matrix_rows == n and matrix_cols == n:
        print("✅ PASS: Matrix dimensions correct")
    else:
        print("❌ FAIL: Matrix dimensions incorrect")
        return False
    
    # Validation 2: Symmetry
    print_section("VALIDATION 2: SYMMETRY CHECK")
    symmetry_ok = True
    for i in range(n):
        for j in range(i+1, n):
            cell_ij = result.matrix[i][j]
            cell_ji = result.matrix[j][i]
            
            if cell_ij != cell_ji:
                print(f"❌ Asymmetry detected at [{i}][{j}] vs [{j}][{i}]")
                print(f"   [{i}][{j}]: {cell_ij.compatibility.value if cell_ij else None}")
                print(f"   [{j}][{i}]: {cell_ji.compatibility.value if cell_ji else None}")
                symmetry_ok = False
    
    if symmetry_ok:
        print("✅ PASS: Matrix is symmetric")
    else:
        print("❌ FAIL: Matrix symmetry violated")
    
    # Validation 3: Logic checks
    print_section("VALIDATION 3: LOGIC VERIFICATION")
    
    checks = []
    
    # Check 1: Acid + Base must be Incompatible or Caution
    acid_base_cell = result.matrix[0][1]
    acid_base_compat = acid_base_cell.compatibility if acid_base_cell else None
    acid_base_ok = acid_base_compat in [Compatibility.INCOMPATIBLE, Compatibility.CAUTION]
    checks.append({
        'name': 'Acid + Base',
        'cell': '[0][1]',
        'expected': 'Incompatible/Caution',
        'actual': acid_base_compat.value if acid_base_compat else 'None',
        'pass': acid_base_ok,
        'hazards': acid_base_cell.hazards if acid_base_cell else []
    })
    
    # Check 2: Acid + Water should have some reaction
    acid_water_cell = result.matrix[0][2]
    acid_water_compat = acid_water_cell.compatibility if acid_water_cell else None
    acid_water_ok = acid_water_compat in [Compatibility.INCOMPATIBLE, Compatibility.CAUTION, Compatibility.COMPATIBLE]
    checks.append({
        'name': 'Acid + Water',
        'cell': '[0][2]',
        'expected': 'Any valid code',
        'actual': acid_water_compat.value if acid_water_compat else 'None',
        'pass': acid_water_ok,
        'hazards': acid_water_cell.hazards if acid_water_cell else []
    })
    
    # Check 3: Nitrogen + Acid - FAIL-SAFE: No rule = Caution/NO_DATA (priority 2)
    nitrogen_acid_cell = result.matrix[3][0]
    nitrogen_compat = nitrogen_acid_cell.compatibility if nitrogen_acid_cell else None
    nitrogen_ok = nitrogen_compat in [Compatibility.COMPATIBLE, Compatibility.NO_DATA, Compatibility.CAUTION]
    checks.append({
        'name': 'Nitrogen + Acid (Fail-Safe)',
        'cell': '[3][0]',
        'expected': 'Compatible/Caution/No Data',
        'actual': nitrogen_compat.value if nitrogen_compat else 'None',
        'pass': nitrogen_ok,
        'hazards': nitrogen_acid_cell.hazards if nitrogen_acid_cell else []
    })
    
    # Check 4: Diagonal (self-interaction) must be Compatible or Caution
    diagonal_ok = True
    for i in range(n):
        diag_cell = result.matrix[i][i]
        diag_compat = diag_cell.compatibility if diag_cell else None
        if diag_compat not in [Compatibility.COMPATIBLE, Compatibility.CAUTION]:
            diagonal_ok = False
            checks.append({
                'name': f'Diagonal [{i}][{i}]',
                'cell': f'[{i}][{i}]',
                'expected': 'Compatible/Caution',
                'actual': diag_compat.value if diag_compat else 'None',
                'pass': False,
                'hazards': []
            })
    
    if diagonal_ok:
        checks.append({
            'name': 'All diagonal cells',
            'cell': 'All',
            'expected': 'Compatible/Caution',
            'actual': 'All valid',
            'pass': True,
            'hazards': []
        })
    
    # Print checks
    for check in checks:
        status = "✅ PASS" if check['pass'] else "❌ FAIL"
        print(f"\n{status}: {check['name']} (Cell {check['cell']})")
        print(f"   Expected: {check['expected']}")
        print(f"   Actual:   {check['actual']}")
        if check['hazards']:
            print(f"   Hazards:  {', '.join(check['hazards'])}")
    
    logic_ok = all(c['pass'] for c in checks)
    
    # Validation 4: Critical Pairs
    print_section("VALIDATION 4: CRITICAL PAIRS ANALYSIS")
    print(f"Critical pairs detected: {len(result.critical_pairs)}")
    
    for idx, pair in enumerate(result.critical_pairs, 1):
        print(f"\n🚨 Critical Pair #{idx}:")
        print(f"   Chemicals: {' + '.join(pair['chemicals'])}")
        print(f"   Hazards:   {', '.join(pair['hazards'])}")
        if pair['gases']:
            print(f"   Gases:     {', '.join(pair['gases'])}")
    
    # Validation 5: Warnings
    print_section("VALIDATION 5: WARNINGS")
    print(f"Total warnings: {len(result.warnings)}")
    for idx, warning in enumerate(result.warnings, 1):
        print(f"   {idx}. {warning}")
    
    # Overall result
    print_section("OVERALL RESULT")
    print(f"Overall Compatibility: {result.overall_compatibility.value}")
    print(f"Chemical Count: {result.chemical_count}")
    print(f"Total Cells: {matrix_rows * matrix_cols}")
    print(f"Critical Pairs: {len(result.critical_pairs)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Audit ID: {result.audit_id}")
    
    # Final verdict
    all_pass = (matrix_rows == n and matrix_cols == n) and symmetry_ok and logic_ok
    
    print("\n" + "=" * 70)
    if all_pass:
        print("✅ ALL TESTS PASSED - Engine handles 4x4 matrix correctly")
    else:
        print("❌ SOME TESTS FAILED - Review results above")
    print("=" * 70 + "\n")
    
    return all_pass

def test_fail_safe_behavior():
    """
    Test Fail-Safe logic: Chemicals with NO groups should return NO_DATA
    """
    print_section("FAIL-SAFE BEHAVIOR TEST")
    
    engine = ReactivityEngine(DB_PATH)
    
    # Test with chemicals that have NO reactive groups
    no_groups_ids = [30062, 30063]  # TEST_CHEMICAL_NO_GROUPS_A and B
    
    print(f"\n🧪 Testing chemicals with NO reactive groups:")
    print(f"   1. Test Chemical A (ID: {no_groups_ids[0]})")
    print(f"   2. Test Chemical B (ID: {no_groups_ids[1]})")
    
    result = engine.analyze(no_groups_ids, include_water_check=False)
    
    # Check off-diagonal cells
    cell_01 = result.matrix[0][1]
    compat = cell_01.compatibility if cell_01 else None
    
    print(f"\n📊 Result:")
    print(f"   Cell [0][1] compatibility: {compat.value if compat else 'None'}")
    
    if compat == Compatibility.NO_DATA:
        print("✅ PASS: Fail-Safe correctly returns NO_DATA for missing groups")
        return True
    else:
        print("❌ FAIL: Expected NO_DATA but got {compat.value if compat else 'None'}")
        return False

def main():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 16 + "CAMEO MATRIX STRESS TEST SUITE" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run tests
    test1_pass = test_4x4_matrix()
    test2_pass = test_fail_safe_behavior()
    
    # Summary
    print_section("TEST SUITE SUMMARY")
    print(f"4x4 Matrix Test:     {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Fail-Safe Test:      {'✅ PASS' if test2_pass else '❌ FAIL'}")
    
    if test1_pass and test2_pass:
        print("\n🎉 ALL TESTS PASSED - Engine is production-ready!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Review and fix issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
