# services/wahapedia-scraper/tests/test_faction_list.py

import sys
sys.path.insert(0, '/app/src/scrapers/wahapedia')
sys.path.insert(0, '/app/src/scrapers/wahapedia/extractors')

from faction_list import FactionListExtractor
import json

def test_faction_extraction():
    """Test the faction list extraction."""
    print("Testing Faction List Extraction")
    print("=" * 50)

    # Create extractor
    extractor = FactionListExtractor()

    # Extract factions
    factions = extractor.extract_factions()

    if factions:
        print(f"✓ Successfully extracted {len(factions)} factions\n")

        # Display first 5 factions as examples
        print("Sample factions:")
        for faction in factions[:5]:
            print(f"  - {faction['name']}")
            print(f"    URL: {faction['url']}")
            print(f"    Code: {faction['code']}")
            print()

        # Check for expected factions
        faction_names = [f['name'] for f in factions]
        expected_factions = [
                'Space Marines',
                'Astra Militarum', 
                'Orks',
                'Aeldari',
                'Necrons'
                ]

        print("Checking for expected factions:")
        for expected in expected_factions:
            if expected in faction_names:
                print(f"  ✓ Found {expected}")
            else:
                print(f"  ✗ Missing {expected}")

        # Save to JSON file for inspection
        output_file = '/app/output/factions.json'
        extractor.save_to_json(output_file)
        print(f"\n✓ Saved full faction list to {output_file}")

    else:
        print("✗ Failed to extract any factions")

    print("=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_faction_extraction()
