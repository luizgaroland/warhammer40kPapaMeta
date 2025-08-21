# services/wahapedia-scraper/tests/test_army_rules.py

import sys
sys.path.insert(0, '/app/src/scrapers/wahapedia')
sys.path.insert(0, '/app/src/scrapers/wahapedia/extractors')

from faction_list import FactionListExtractor
from army_rules import ArmyRulesExtractor
import json

def test_single_faction_army_rule():
    """Test extracting army rule for a single faction."""
    print("Testing Single Faction Army Rule Extraction")
    print("=" * 50)

    # Test with a specific faction
    test_faction = {
            'name': 'Adeptus Custodes',
            'url': 'https://wahapedia.ru/wh40k10ed/factions/adeptus-custodes',
            'code': 'adeptus-custodes'
            }

    extractor = ArmyRulesExtractor(publish_to_redis=False)
    result = extractor.extract_army_rule_for_faction(test_faction)

    if result:
        print(f"✓ Successfully extracted army rule")
        print(f"  Faction: {result['faction_name']}")
        print(f"  Army Rule: {result['army_rule_name']}")
    else:
        print(f"✗ Failed to extract army rule for {test_faction['name']}")

    return result

def test_all_factions_army_rules(limit=None):
    """
    Test extracting army rules for all factions.

    Args:
        limit: Number of factions to process (None for all)
    """
    print("\nTesting All Factions Army Rules Extraction")
    print("=" * 50)

    # First get all factions
    print("Getting faction list...")
    faction_extractor = FactionListExtractor()
    factions = faction_extractor.extract_factions()

    if not factions:
        print("✗ Failed to get faction list")
        return

    print(f"Found {len(factions)} factions total")

    # Apply limit if specified
    if limit:
        test_factions = factions[:limit]
        print(f"\nProcessing first {len(test_factions)} factions")
    else:
        test_factions = factions
        print(f"\nProcessing ALL {len(test_factions)} factions")
        print("⚠️  This will take several minutes due to rate limiting...")

    # Extract army rules
    print("\nExtracting army rules...")
    army_rules_extractor = ArmyRulesExtractor(publish_to_redis=True)
    army_rules = army_rules_extractor.extract_all_army_rules(test_factions)

    if army_rules:
        print(f"\n✓ Successfully extracted {len(army_rules)} army rules:")

        # Group by success
        successful = len(army_rules)
        failed = len(test_factions) - successful

        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")

        # Show all results
        print("\nExtracted Army Rules:")
        print("-" * 50)
        for rule in army_rules:
            print(f"  {rule['faction_name']:30} → {rule['army_rule_name']}")

        # Save to file
        output_file = '/app/output/army_rules_complete.json'
        army_rules_extractor.save_to_json(output_file)
        print(f"\n✓ Saved results to {output_file}")
    else:
        print("✗ Failed to extract any army rules")

    return army_rules

def extract_all_army_rules():
    """Main function to extract ALL army rules."""
    print("FULL Army Rules Extraction")
    print("=" * 70)
    print("This will extract army rules for ALL factions.")
    print("Expected time: 2-3 minutes (with rate limiting)")
    print("=" * 70)

    results = test_all_factions_army_rules(limit=None)  # No limit - get all

    if results:
        print("\n" + "=" * 70)
        print(f"✓ Extraction complete! Found {len(results)} army rules")
    else:
        print("\n✗ Extraction failed")

    return results

if __name__ == "__main__":
    import sys

    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Extract ALL factions
        extract_all_army_rules()
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        # Extract specified number of factions
        limit = int(sys.argv[1])
        print(f"Extracting army rules for {limit} factions...")
        test_all_factions_army_rules(limit=limit)
    else:
        # Default: test with 3 factions
        print("Testing with 3 factions (use --all for all factions)")
        print("-" * 50)
        test_single_faction_army_rule()
        test_all_factions_army_rules(limit=3)
