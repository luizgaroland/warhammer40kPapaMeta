# services/web-scraper/src/services/wahapedia/wahapedia_service.py
"""
Wahapedia implementation of the scraper service
"""
import sys
sys.path.insert(0, "/app/src")

from typing import List, Dict, Any, Optional
from src.utils.logging import get_logger

from core.base_scraper_service import BaseScraperService
from core.scraper_context import ScraperContext
from services.url_config import WahapediaURLConfig

logger = get_logger(__name__)

class WahapediaService(BaseScraperService):
    """
    Wahapedia-specific implementation of the scraper service.
    Uses existing extractors but provides the generic interface.
    """

    def __init__(self, context: ScraperContext):
        """
        Initialize Wahapedia service.

        Args:
            context: Scraper context with version info
        """
        super().__init__(context)
        self.url_config = WahapediaURLConfig(self.version_id)
        self.scraper = BaseScraper()

        # Import extractors lazily to avoid circular dependencies
        self._faction_extractor = None
        self._army_rules_extractor = None

        logger.info(
                "wahapedia_service_initialized",
                version_id=self.version_id,
                url_path=self.url_config.get_version_path()
                )

    def _get_faction_extractor(self):
        """Lazy load faction extractor."""
        if not self._faction_extractor:
            from src.scrapers.wahapedia.extractors.faction_list import FactionListExtractor
            self._faction_extractor = FactionListExtractor(publish_to_redis=False)
        return self._faction_extractor

    def _get_army_rules_extractor(self):
        """Lazy load army rules extractor."""
        if not self._army_rules_extractor:
            from src.scrapers.wahapedia.extractors.army_rules import ArmyRulesExtractor
            self._army_rules_extractor = ArmyRulesExtractor(publish_to_redis=False)
        return self._army_rules_extractor

    def get_factions(self) -> List[Dict[str, Any]]:
        """
        Get all factions from Wahapedia.

        Returns:
            List of faction dictionaries
        """
        logger.info("getting_factions_from_wahapedia")

        # Use existing faction extractor
        extractor = self._get_faction_extractor()

        # Override the URL with our version-aware URL
        original_url = "/wh40k10ed/the-rules/quick-start-guide/"
        new_url = self.url_config.get_quick_start_url()

        # Temporarily patch the fetch_and_parse to use our URL
        original_fetch = extractor.fetch_and_parse

        def versioned_fetch(url):
            if url == original_url:
                url = new_url
            return original_fetch(url)

        extractor.fetch_and_parse = versioned_fetch

        # Extract factions
        factions = extractor.extract_factions()

        # Add source to each faction
        for faction in factions:
            faction['source'] = 'wahapedia'
            faction['version_id'] = self.version_id

        logger.info(f"extracted_factions", count=len(factions))
        return factions

    def get_army_rules(self, faction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get army rules for a faction.

        Args:
            faction: Faction dictionary

        Returns:
            Army rules dictionary
        """
        if not self.validate_faction_dict(faction):
            logger.warning("invalid_faction_dict", faction=faction)
            return None

        logger.info(
                "getting_army_rules",
                faction=faction.get('name')
                )

        extractor = self._get_army_rules_extractor()
        result = extractor.extract_army_rule_for_faction(faction)

        if result:
            result['source'] = 'wahapedia'
            result['version_id'] = self.version_id

        return result

    def get_detachments(self, faction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get detachments for a faction.
        TODO: Implement when detachment extractor is ready
        """
        logger.info(
                "getting_detachments",
                faction=faction.get('name')
                )

        # Placeholder - implement when detachment extractor is ready
        return []

    def get_enhancements(self, detachment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get enhancements for a detachment.
        TODO: Implement when enhancement extractor is ready
        """
        logger.info(
                "getting_enhancements",
                detachment=detachment.get('name')
                )

        # Placeholder - implement when enhancement extractor is ready
        return []

    def get_units(self, faction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get units for a faction.
        TODO: Implement when unit extractor is ready
        """
        logger.info(
                "getting_units",
                faction=faction.get('name')
                )

        # Placeholder - implement when unit extractor is ready
        return []

    def get_wargear(self, unit: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get wargear for a unit.
        TODO: Implement when wargear extractor is ready
        """
        logger.info(
                "getting_wargear",
                unit=unit.get('name')
                )

        # Placeholder - implement when wargear extractor is ready
        return []
