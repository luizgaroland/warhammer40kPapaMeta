# services/wahapedia-scraper/src/scrapers/wahapedia/extractors/faction_list.py

import sys
sys.path.insert(0, '/app/src/scrapers/wahapedia')
sys.path.insert(0, '/app/src/publishers')

from typing import List, Dict, Optional
import json
from base_scraper import BaseScraper
from css_selectors import FACTION_SELECTORS, URLS
from scraper_publisher import ScraperPublisher

class FactionListExtractor(BaseScraper):
    """Extractor for getting all faction names and URLs from Wahapedia."""

    def __init__(self, publish_to_redis: bool = True):
        """
        Initialize the faction list extractor.

        Args:
            publish_to_redis: Whether to publish results to Redis
        """
        super().__init__()
        self.factions = []
        self.publish_to_redis = publish_to_redis

        if self.publish_to_redis:
            self.publisher = ScraperPublisher()

    def extract_factions(self) -> List[Dict[str, str]]:
        """
        Extract all faction names and URLs from the navigation dropdown.

        Returns:
            List of dictionaries containing faction name and URL
        """
        self.logger.info("Starting faction extraction...")

        # Publish start status if Redis is enabled
        if self.publish_to_redis:
            self.publisher.publish_status('started', {'task': 'faction_extraction'})

        # Fetch the quick start page which has the faction dropdown
        soup = self.fetch_and_parse(URLS['quick_start'])

        if not soup:
            self.logger.error("Failed to fetch quick start page")
            if self.publish_to_redis:
                self.publisher.publish_status('error', {
                    'task': 'faction_extraction',
                    'error': 'Failed to fetch quick start page'
                    })
            return []

        # Find the faction navigation button
        faction_btn = soup.select_one(FACTION_SELECTORS['nav_button'])

        if not faction_btn:
            self.logger.error("Could not find faction navigation button")
            if self.publish_to_redis:
                self.publisher.publish_status('error', {
                    'task': 'faction_extraction',
                    'error': 'Could not find faction navigation button'
                    })
            return []

        # The dropdown content is actually present in the HTML,
        # just hidden by CSS until hover
        # We need to find it relative to the nav button

        # Find the dropdown content (it's a sibling)
        dropdown = None
        for sibling in faction_btn.find_next_siblings():
            if 'NavDropdown-content' in sibling.get('class', []):
                dropdown = sibling
                break

        if not dropdown:
            self.logger.error("Could not find faction dropdown content")
            if self.publish_to_redis:
                self.publisher.publish_status('error', {
                    'task': 'faction_extraction',
                    'error': 'Could not find faction dropdown content'
                    })
            return []

        self.logger.info("Found faction dropdown content")

        # Extract all faction links
        faction_links = dropdown.select(FACTION_SELECTORS['faction_link'])

        self.logger.info(f"Found {len(faction_links)} factions")

        for link in faction_links:
            faction_name = self.safe_extract_text(link)
            faction_url = self.safe_extract_attribute(link, 'href')

            if faction_name and faction_url:
                # Clean up the faction name (remove any extra whitespace)
                faction_name = faction_name.strip()

                # Convert relative URL to absolute if needed
                if not faction_url.startswith('http'):
                    faction_url = f"{self.BASE_URL}{faction_url}"

                faction_data = {
                        'name': faction_name,
                        'url': faction_url,
                        'code': self._extract_faction_code(faction_url)
                        }

                self.factions.append(faction_data)
                self.logger.debug(f"Extracted faction: {faction_name}")

        self.logger.info(f"Successfully extracted {len(self.factions)} factions")

        # Publish to Redis if enabled and we have factions
        if self.publish_to_redis and self.factions:
            success = self.publisher.publish_factions(self.factions)
            if success:
                self.publisher.publish_status('completed', {
                    'task': 'faction_extraction',
                    'faction_count': len(self.factions)
                    })
            else:
                self.publisher.publish_status('error', {
                    'task': 'faction_extraction',
                    'error': 'Failed to publish to Redis'
                    })

        return self.factions

    def _extract_faction_code(self, url: str) -> str:
        """
        Extract faction code from URL.
        Example: /wh40k10ed/factions/space-marines/ -> space-marines

        Args:
            url: Faction URL

        Returns:
            Faction code string
        """
        parts = url.rstrip('/').split('/')
        if 'factions' in parts:
            faction_index = parts.index('factions')
            if faction_index + 1 < len(parts):
                return parts[faction_index + 1]
        return ""

    def save_to_json(self, filename: str = 'factions.json'):
        """
        Save extracted factions to a JSON file.

        Args:
            filename: Output filename
        """
        if not self.factions:
            self.logger.warning("No factions to save")
            return

        try:
            with open(filename, 'w') as f:
                json.dump(self.factions, f, indent=2)
            self.logger.info(f"Saved {len(self.factions)} factions to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
