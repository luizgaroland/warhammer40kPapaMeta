# services/web-scraper/src/scrapers/wahapedia/test_base.py

import sys
sys.path.insert(0, '/app/src/scrapers/wahapedia')

from base_scraper import BaseScraper
import time

def test_basic_connection():
    """Test that we can connect to Wahapedia and fetch a page."""
    scraper = BaseScraper()

    # Try to fetch the quick start guide page
    url = "/wh40k10ed/the-rules/quick-start-guide/"
    soup = scraper.fetch_and_parse(url)

    if soup:
        print("✓ Successfully fetched and parsed page")

        # Look for the title
        title = soup.find('title')
        if title:
            print(f"  Page title: {title.text.strip()}")

        # Look for faction dropdown
        faction_btn = soup.select_one('.NavBtn_Factions')
        if faction_btn:
            print("✓ Found faction navigation button")

            # Find the dropdown content
            # The dropdown is a sibling of the button's parent
            nav_item = faction_btn.find_parent('div')
            if nav_item:
                dropdown = nav_item.find_next_sibling('div', class_='NavDropdown-content')
                if dropdown:
                    print("✓ Found faction dropdown content")
                    # Count factions
                    faction_links = dropdown.select('.BreakInsideAvoid a')
                    print(f"  Found {len(faction_links)} factions")
    else:
        print("✗ Failed to fetch or parse page")

def test_rate_limiting():
    """Test that rate limiting works."""
    scraper = BaseScraper(rate_limit_min=2.0, rate_limit_max=3.0)

    print("\nTesting rate limiting (should take 2-3 seconds)...")
    start = time.time()

    # Make two requests
    scraper.fetch_page("/wh40k10ed/the-rules/quick-start-guide/")
    scraper.fetch_page("/wh40k10ed/the-rules/quick-start-guide/")

    elapsed = time.time() - start
    print(f"✓ Two requests took {elapsed:.2f} seconds")

    if elapsed >= 2.0:
        print("  Rate limiting is working correctly")
    else:
        print("  Warning: Rate limiting might not be working")

if __name__ == "__main__":
    print("Testing Base Scraper...")
    print("=" * 50)
    test_basic_connection()
    test_rate_limiting()
    print("=" * 50)
    print("Base scraper tests complete!")
