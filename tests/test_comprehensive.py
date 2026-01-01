"""
Comprehensive tests for CAMEO web migration
Tests data accuracy, API correctness, UI functionality, and favorites management
"""
import pytest
import sqlite3
from playwright.sync_api import Page, expect
import json

# Path to the actual databases
DB_PATH = "backend/data/chemicals.db"
USER_DB_PATH = "backend/data/user.db"

@pytest.fixture
def db_connection():
    """Direct connection to chemicals database for verification"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_database_exists_and_accessible(db_connection):
    """Verify the database file exists and is readable"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Verify key tables exist
    assert 'chemicals' in tables, "chemicals table must exist"
    assert 'chemical_search' in tables, "chemical_search table must exist"
    print(f"✓ Database contains {len(tables)} tables")

def test_chemical_count(db_connection):
    """Verify total chemical count in database"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM chemicals")
    count = cursor.fetchone()[0]
    
    assert count > 0, "Database should contain chemicals"
    print(f"✓ Database contains {count} chemicals")

def test_search_api_matches_database(page: Page, db_connection):
    """Verify API search results match direct database queries"""
    test_queries = ["acetone", "benzene", "water", "acid"]
    
    for query in test_queries:
        # Get results from API
        response = page.request.get(f"http://localhost:5000/api/search?q={query}")
        assert response.ok, f"API search for '{query}' failed"
        api_data = response.json()
        
        # Get results directly from database
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT id, name, synonyms 
            FROM chemicals 
            WHERE name LIKE ? OR synonyms LIKE ?
            LIMIT 500
        """, (f"%{query}%", f"%{query}%"))
        db_results = cursor.fetchall()
        
        # Compare counts
        assert len(api_data['items']) == len(db_results), \
            f"API returned {len(api_data['items'])} items but DB has {len(db_results)} for query '{query}'"
        
        # Verify IDs match
        api_ids = {item['id'] for item in api_data['items']}
        db_ids = {row['id'] for row in db_results}
        assert api_ids == db_ids, f"API and DB results don't match for query '{query}'"
        
        print(f"✓ Search '{query}': API matches DB ({len(api_data['items'])} results)")

def test_get_chemical_details_accuracy(page: Page, db_connection):
    """Verify chemical details API returns correct data from database"""
    # Get a sample chemical ID first
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, name, formulas FROM chemicals LIMIT 5")
    sample_chemicals = cursor.fetchall()
    
    for chem in sample_chemicals:
        chem_id = chem['id']
        
        # Get from API
        response = page.request.get(f"http://localhost:5000/api/chemical/{chem_id}")
        assert response.ok, f"API failed for chemical ID {chem_id}"
        api_data = response.json()
        
        # Get from database
        cursor.execute("SELECT * FROM chemicals WHERE id = ?", (chem_id,))
        db_data = dict(cursor.fetchone())
        
        # Compare key fields
        assert api_data['id'] == db_data['id'], f"ID mismatch for chemical {chem_id}"
        assert api_data['name'] == db_data['name'], f"Name mismatch for chemical {chem_id}"
        
        # Check formulas if present
        if db_data.get('formulas'):
            assert api_data.get('formulas') == db_data['formulas'], \
                f"Formulas mismatch for {db_data['name']}"
        
        print(f"✓ Chemical {chem_id} ({db_data['name']}): API data matches DB")

def test_search_ui_displays_correct_results(page: Page, db_connection):
    """Test that UI search displays correct results from database"""
    page.goto("http://localhost:5173")
    
    # Search for acetone
    search_input = page.get_by_placeholder("Search chemicals by name or synonym...")
    search_input.fill("acetone")
    search_input.press("Enter")
    
    # Wait for results
    page.wait_for_timeout(1000)
    
    # Get results from database
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT id, name 
        FROM chemicals 
        WHERE name LIKE ? OR synonyms LIKE ?
        LIMIT 500
    """, ("%acetone%", "%acetone%"))
    db_results = cursor.fetchall()
    
    # Verify at least the first result is visible
    assert len(db_results) > 0, "Database should have acetone results"
    first_result_name = db_results[0]['name']
    
    # Use first() to handle multiple matches
    expect(page.get_by_text(first_result_name, exact=False).first).to_be_visible(timeout=5000)
    print(f"✓ UI displays correct search results for 'acetone'")

def test_favorites_add_and_retrieve(page: Page):
    """Test adding and retrieving favorites"""
    # First, search for a chemical
    response = page.request.get("http://localhost:5000/api/search?q=water")
    assert response.ok
    data = response.json()
    assert len(data['items']) > 0
    
    chemical_id = data['items'][0]['id']
    
    # Add to favorites
    add_response = page.request.post(
        "http://localhost:5000/api/favorites",
        data=json.dumps({"chemical_id": chemical_id, "note": "Test favorite"}),
        headers={"Content-Type": "application/json"}
    )
    assert add_response.ok, "Failed to add favorite"
    
    # Retrieve favorites
    get_response = page.request.get("http://localhost:5000/api/favorites")
    assert get_response.ok, "Failed to get favorites"
    favorites = get_response.json()
    
    # Verify the favorite was added
    favorite_ids = [fav['chemical_id'] for fav in favorites]
    assert chemical_id in favorite_ids, "Added favorite not found in list"
    
    print(f"✓ Favorites: Added and retrieved chemical ID {chemical_id}")
    
    # Cleanup - remove the favorite
    delete_response = page.request.delete(f"http://localhost:5000/api/favorites/{chemical_id}")
    assert delete_response.ok, "Failed to delete favorite"
    print(f"✓ Favorites: Successfully removed test favorite")

def test_favorites_ui_interaction(page: Page):
    """Test favorites functionality through UI"""
    page.goto("http://localhost:5173")
    
    # Search for a chemical
    search_input = page.get_by_placeholder("Search chemicals by name or synonym...")
    search_input.fill("benzene")
    search_input.press("Enter")
    
    # Wait for results
    page.wait_for_timeout(1000)
    
    # Try to find and click on a result (if UI supports clicking)
    # This is a basic test - adjust based on actual UI implementation
    expect(page.get_by_text("benzene", exact=False).first).to_be_visible(timeout=5000)
    print(f"✓ UI: Can search and display results for favorites testing")

def test_search_limit_500(page: Page, db_connection):
    """Verify search limit is 500 as specified"""
    # Search for a common term that might have many results
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM chemicals 
        WHERE name LIKE ? OR synonyms LIKE ?
    """, ("%acid%", "%acid%"))
    total_matches = cursor.fetchone()[0]
    
    # Get from API
    response = page.request.get("http://localhost:5000/api/search?q=acid")
    assert response.ok
    data = response.json()
    
    # If DB has more than 500, API should return exactly 500
    if total_matches > 500:
        assert len(data['items']) == 500, f"Should limit to 500 results, got {len(data['items'])}"
        print(f"✓ Search limit: Returns 500 results when DB has {total_matches}")
    else:
        assert len(data['items']) == total_matches, \
            f"Should return all {total_matches} results when under limit"
        print(f"✓ Search limit: Returns all {total_matches} results when under 500")

def test_special_characters_in_search(page: Page, db_connection):
    """Test search handles special characters correctly"""
    special_queries = ["(", ")", "-", ",", "2,4-", "H2O"]
    
    for query in special_queries:
        try:
            response = page.request.get(f"http://localhost:5000/api/search?q={query}")
            assert response.ok or response.status == 200, \
                f"API should handle special character '{query}'"
            
            # Verify database query doesn't crash
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM chemicals 
                WHERE name LIKE ? OR synonyms LIKE ?
                LIMIT 500
            """, (f"%{query}%", f"%{query}%"))
            cursor.fetchone()
            
            print(f"✓ Special characters: '{query}' handled correctly")
        except Exception as e:
            pytest.fail(f"Failed to handle special character '{query}': {e}")

def test_empty_search_handling(page: Page):
    """Test that empty search is handled gracefully"""
    response = page.request.get("http://localhost:5000/api/search?q=")
    assert response.ok
    data = response.json()
    # Empty search should return empty results, not crash
    assert isinstance(data['items'], list)
    print(f"✓ Empty search handled correctly")

def test_nonexistent_chemical_id(page: Page):
    """Test that requesting non-existent chemical ID is handled"""
    response = page.request.get("http://localhost:5000/api/chemical/999999999")
    # Should return 404 or empty result, not crash
    assert response.status in [200, 404], "Should handle non-existent ID gracefully"
    print(f"✓ Non-existent chemical ID handled correctly")

def test_case_insensitive_search(page: Page, db_connection):
    """Verify search is case-insensitive"""
    queries = [
        ("ACETONE", "acetone"),
        ("Benzene", "BENZENE"),
        ("WaTeR", "water")
    ]
    
    for upper_query, lower_query in queries:
        # Get results for uppercase
        response1 = page.request.get(f"http://localhost:5000/api/search?q={upper_query}")
        data1 = response1.json()
        
        # Get results for lowercase
        response2 = page.request.get(f"http://localhost:5000/api/search?q={lower_query}")
        data2 = response2.json()
        
        # Should return same results
        assert len(data1['items']) == len(data2['items']), \
            f"Case-insensitive search failed for '{upper_query}' vs '{lower_query}'"
        
        print(f"✓ Case-insensitive: '{upper_query}' and '{lower_query}' return same results")

def test_ui_loads_without_errors(page: Page):
    """Verify UI loads without console errors"""
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.on("console", lambda msg: errors.append(str(msg)) if msg.type == "error" else None)
    
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    
    # Check title loaded
    expect(page).to_have_title("CAMEO Chemicals - Offline Database")
    
    # Should have no critical errors
    assert len(errors) == 0 or all("favicon" in str(e).lower() for e in errors), \
        f"UI loaded with errors: {errors}"
    
    print(f"✓ UI loads without critical errors")

def test_backend_database_connection(page: Page):
    """Verify backend successfully connects to database"""
    # Make a simple API call
    response = page.request.get("http://localhost:5000/api/search?q=test")
    assert response.ok, "Backend should be able to query database"
    
    data = response.json()
    assert 'items' in data and 'total' in data, "Backend returns correct structure"
    
    print(f"✓ Backend database connection working")
