import pytest
from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    # Assuming frontend runs on port 5173
    page.goto("http://localhost:5173")
    expect(page).to_have_title("CAMEO Chemicals - Offline Database")

def test_search_functionality(page: Page):
    page.goto("http://localhost:5173")
    
    # Wait for search input and type 'acetone'
    search_input = page.get_by_placeholder("Search chemicals by name or synonym...")
    search_input.fill("acetone")
    
    # Trigger search - press Enter or wait for auto-search
    search_input.press("Enter")
    
    # Wait for results with a longer timeout
    # Assuming results are displayed in a list
    expect(page.get_by_text("Acetone", exact=False).first).to_be_visible(timeout=10000)

def test_backend_api_direct(page: Page):
    # Test that the backend API is reachable directly
    response = page.request.get("http://localhost:5000/api/search?q=acetone")
    expect(response).to_be_ok()
    data = response.json()
    assert data['total'] > 0
    # Case-insensitive check
    assert any("acetone" in item['name'].lower() for item in data['items'])
