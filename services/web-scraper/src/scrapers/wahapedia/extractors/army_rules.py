# services/web-scraper/src/scrapers/wahapedia/extractors/army_rules.py

import sys
sys.path.insert(0, '/app/src/scrapers/wahapedia')
sys.path.insert(0, '/app/src/publishers')

from typing import List, Dict, Optional
import json
from base_scraper import BaseScraper
from css_selectors import ARMY_RULE_SELECTORS
from scraper_publisher import ScraperPublisher
from redis_client import redis_manager

class ArmyRulesExtractor(BaseScraper):
    """Extractor for getting army rules for each faction."""

    def __init__(self, publish_to_redis: bool = True):
        """
        Initialize the army rules extractor.

        Args:
            publish_to_redis: Whether to publish results to Redis
        """
        super().__init__()
        self.army_rules = []
        self.publish_to_redis = publish_to_redis

        if self.publish_to_redis:
            self.publisher = ScraperPublisher()

    def extract_army_rule_for_faction(self, faction_data: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Extract army rule for a specific faction.

        Args:
            faction_data: Dictionary with faction name, url, and code

        Returns:
            Dictionary with faction info and army rule, or None if failed
        """
        faction_name = faction_data.get('name')
        faction_url = faction_data.get('url')
        faction_code = faction_data.get('code')

        if not faction_url:
            self.logger.error(f"No URL for faction {faction_name}")
            return None

        self.logger.info(f"Extracting army rule for {faction_name}")

        # Fetch the faction page
        soup = self.fetch_and_parse(faction_url)

        if not soup:
            self.logger.error(f"Failed to fetch page for {faction_name}")
            return None

        # Find the Army Rules anchor
        army_rules_anchor = soup.find('a', {'name': 'Army-Rules'})

        if not army_rules_anchor:
            self.logger.warning(f"No Army Rules anchor found for {faction_name}")
            return None

        target = army_rules_anchor
        # Try to find the next Columns2 div after the anchor
        for sibling in target.find_next_siblings():
            if sibling.name == 'div' and 'Columns2' in sibling.get('class', []):
                target = sibling
                break

        if target == army_rules_anchor:
            self.logger.warning(f"No Columns2 div found after Army Rules anchor for {faction_name} switching to BreakInsideAvoid directly")
            # Find the BreakInsideAvoid div
            break_div = None
            for sibling in target.find_next_siblings():
                if sibling.name == 'div' and 'BreakInsideAvoid' in sibling.get('class', []):
                    break_div = sibling
                    break

            if not break_div:
                self.logger.warning(f"No BreakInsideAvoid div found for {faction_name}")
                return None
        else:
            break_div = target.find('div', {'class': 'BreakInsideAvoid'})

            if not break_div:
                self.logger.warning(f"No BreakInsideAvoid div found for {faction_name}")
                return None

        # Army name
        # Find the first h3 tag
        army_rule_header = break_div.find('h3')

        if not army_rule_header:
            self.logger.warning(f"No h3 tag found in army rules section for {faction_name}")
            army_rule_header = break_div.find('h2')

            if not army_rule_header:
                self.logger.warning(f"No h2 tag found in army rules section for {faction_name}")
                return None

        army_rule_name = self.safe_extract_text(army_rule_header)

        if army_rule_name:
            result = {
                    'faction_name': faction_name,
                    'faction_code': faction_code,
                    'faction_url': faction_url,
                    'army_rule_name': army_rule_name
                    }

            self.logger.info(f"Found army rule for {faction_name}: {army_rule_name}")
            return result

        return None

    def extract_all_army_rules(self, factions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Extract army rules for all provided factions.

        Args:
            factions: List of faction dictionaries from faction_list extractor

        Returns:
            List of dictionaries with faction info and army rules
        """
        self.logger.info(f"Starting army rules extraction for {len(factions)} factions")

        if self.publish_to_redis:
            self.publisher.publish_status('started', {'task': 'army_rules_extraction'})

        for faction in factions:
            army_rule_data = self.extract_army_rule_for_faction(faction)

            if army_rule_data:
                self.army_rules.append(army_rule_data)
            else:
                self.logger.warning(f"Failed to extract army rule for {faction.get('name')}")

        self.logger.info(f"Successfully extracted {len(self.army_rules)} army rules")

        # Publish to Redis if enabled
        if self.publish_to_redis and self.army_rules:
            self.publish_army_rules()

        return self.army_rules

    def publish_army_rules(self):
        """Publish army rules to Redis."""
        try:
            message = {
                'type': 'army_rules',
                'count': len(self.army_rules),
                'data': self.army_rules
            }

            # Use redis_manager directly instead of self.publisher.redis_manager
            success = redis_manager.publish_message(
                'wahapedia:army_rules',
                message
            )

            if success:
                self.publisher.publish_status('completed', {
                    'task': 'army_rules_extraction',
                    'rules_count': len(self.army_rules)
                })
            else:
                self.publisher.publish_status('error', {
                    'task': 'army_rules_extraction',
                    'error': 'Failed to publish to Redis'
                })

        except Exception as e:
            self.logger.error(f"Error publishing army rules: {str(e)}")

    def save_to_json(self, filename: str = 'army_rules.json'):
        """
        Save extracted army rules to a JSON file.

        Args:
            filename: Output filename
        """
        if not self.army_rules:
            self.logger.warning("No army rules to save")
            return

        try:
            with open(filename, 'w') as f:
                json.dump(self.army_rules, f, indent=2)
            self.logger.info(f"Saved {len(self.army_rules)} army rules to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
