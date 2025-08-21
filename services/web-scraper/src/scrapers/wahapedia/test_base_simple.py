# services/web-scraper/src/scrapers/wahapedia/test_base_simple.py

import sys
sys.path.insert(0, '/app/src')

# Create a minimal test without using the logging module
import time
import requests
from bs4 import BeautifulSoup

def test_basic_fetch():
    """Test basic fetching without the full scraper class."""
    print("Testing basic connection to Wahapedia...")
    
    url = "https://wahapedia.ru/wh40k10ed/the-rules/quick-start-guide/"
    
    try:
        # Simple fetch
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print(f"✓ Successfully fetched page")
        print(f"  Status code: {response.status_code}")
        print(f"  Page size: {len(response.content)} bytes")
        
        # Try to parse
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"  Page title: {title.text.strip()}")
            
        # Look for faction dropdown
        faction_btn = soup.select_one('.NavBtn_Factions')
        if faction_btn:
            print("✓ Found faction navigation button")
        else:
            print("✗ Could not find faction navigation button")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    test_basic_fetch()
