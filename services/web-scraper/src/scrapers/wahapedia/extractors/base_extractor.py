# services/web-scraper/src/scrapers/wahapedia/extractors/base_extractor.py

from typing import Optional
from services.wahapedia.url_config import WahapediaURLConfig
from scrapers.wahapedia.base_scraper import BaseScraper

class BaseExtractor(BaseScraper):
    """Base extractor with URL configuration support."""

    def __init__(self, version_id: str = "10th", publish_to_redis: bool = True):
        super().__init__()
        self.url_config = WahapediaURLConfig(version_id)
        self.publish_to_redis = publish_to_redis
        self.version_id = version_id

    def get_url_for_faction(self, faction_code: str) -> str:
        """Get versioned URL for faction."""
        return self.url_config.get_faction_url(faction_code)
