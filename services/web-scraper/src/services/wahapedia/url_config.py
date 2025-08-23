# services/web-scraper/src/services/wahapedia/url_config.py
"""
Wahapedia URL Configuration
Maps generic version IDs to Wahapedia-specific URL patterns
"""

import sys
sys.path.insert(0, "/app/src")

from typing import Dict, Optional
from src.utils.logging import get_logger

logger = get_logger(__name__)


class WahapediaURLConfig:
    """
    Manages URL patterns for Wahapedia based on game version.
    Translates generic version IDs to Wahapedia URL structures.
    """

    # Map generic version IDs to Wahapedia URL paths
    VERSION_URL_MAPPING = {
            "10th": "wh40k10ed",
            "9th": "wh40k9ed",
            "8th": "wh40k8ed",
            }

    BASE_URL = "https://wahapedia.ru"

    def __init__(self, version_id: str):
        """
        Initialize URL configuration.

        Args:
            version_id: Generic version ID (e.g., "10th")
        """
        self.version_id = version_id
        self.url_path = self.VERSION_URL_MAPPING.get(
                version_id, 
                "wh40k10ed"  # Default to 10th
                )

        logger.debug(
                "wahapedia_url_config_initialized",
                version_id=version_id,
                url_path=self.url_path
                )

    def get_base_url(self) -> str:
        """Get the base Wahapedia URL."""
        return self.BASE_URL

    def get_version_path(self) -> str:
        """Get the version-specific path component."""
        return self.url_path

    def get_quick_start_url(self) -> str:
        """Get URL for quick start guide (has faction dropdown)."""
        return f"{self.BASE_URL}/{self.url_path}/the-rules/quick-start-guide/"

    def get_faction_url(self, faction_code: str) -> str:
        """
        Get URL for a specific faction.

        Args:
            faction_code: Faction code (e.g., "space-marines")

        Returns:
            Full URL to faction page
        """
        return f"{self.BASE_URL}/{self.url_path}/factions/{faction_code}"

    def get_faction_datasheets_url(self, faction_code: str) -> str:
        """
        Get URL for faction datasheets.

        Args:
            faction_code: Faction code

        Returns:
            URL to faction datasheets page
        """
        return f"{self.BASE_URL}/{self.url_path}/factions/{faction_code}/datasheets.html"

    def get_army_lists_url(self) -> str:
        """Get URL for army lists page."""
        return f"{self.BASE_URL}/{self.url_path}/army-lists/"

    def build_url(self, path: str) -> str:
        """
        Build a full URL from a relative path.

        Args:
            path: Relative path (e.g., "/factions/")

        Returns:
            Full URL
        """
        if path.startswith('/'):
            path = path[1:]
        return f"{self.BASE_URL}/{self.url_path}/{path}"
