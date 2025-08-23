# services/web-scraper/src/services/wahapedia/url_config.py
"""
Wahapedia URL Configuration
Maps generic version IDs to Wahapedia-specific URL patterns
"""

import sys
sys.path.insert(0, "/app/src")

from typing import Dict, Optional, List, Set
from urllib.parse import urlencode, quote
import re
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

    # Comprehensive URL pattern registry
    URL_PATTERNS = {
            # Navigation/Base Pages
            'quick_start': '/{version}/the-rules/quick-start-guide/',
            'factions_index': '/{version}/factions/',
            'core_rules': '/{version}/the-rules/core-rules/',
            'missions': '/{version}/the-rules/missions/',

            # Faction-specific Pages
            'faction_main': '/{version}/factions/{faction_code}',
            'faction_datasheets': '/{version}/factions/{faction_code}/datasheets',
            'faction_stratagems': '/{version}/factions/{faction_code}/stratagems',
            'faction_index': '/{version}/factions/{faction_code}/index.html',

            # Unit-specific
            'unit_datasheet': '/{version}/factions/{faction_code}/datasheets#{unit_slug}',

            # Search/Filters
            'search': '/{version}/search',  # Query params added separately

            # Army Lists
            'army_lists': '/{version}/army-lists/',
            'army_list_builder': '/{version}/army-lists/builder/',
            }

    # Section anchor mappings for different page sections
    SECTION_ANCHORS = {
            'army_rules': 'Army-Rules',
            'detachments': 'Detachment-Rules',
            'detachment_rule': 'Detachment-Rule',  # Some factions use singular
            'enhancements': 'Enhancements',
            'stratagems': 'Stratagems',
            'wargear_options': 'Wargear-Options',
            'unit_composition': 'Unit-Composition',
            'abilities': 'Abilities',
            'keywords': 'Keywords',
            'faction_keywords': 'Faction-Keywords',
            'damaged': 'Damaged',
            'invulnerable_save': 'Invulnerable-Save',
            }

    # Mapping extractors to their required URL patterns
    EXTRACTOR_URL_MAPPING = {
            'FactionListExtractor': ['quick_start'],
            'ArmyRulesExtractor': ['faction_main'],
            'DetachmentsExtractor': ['faction_main'],
            'EnhancementsExtractor': ['faction_main'],
            'UnitsExtractor': ['faction_datasheets'],
            'WargearExtractor': ['faction_datasheets'],
            'StratagemsExtractor': ['faction_stratagems'],
            }

    # Known faction code transformations
    FACTION_CODE_MAPPINGS = {
            "T'au Empire": "t-au-empire",
            "Emperor's Children": "emperor-s-children",
            "Adepta Sororitas": "adepta-sororitas",
            "Adeptus Custodes": "adeptus-custodes",
            "Adeptus Mechanicus": "adeptus-mechanicus",
            "Adeptus Titanicus": "adeptus-titanicus",
            "Astra Militarum": "astra-militarum",
            "Chaos Daemons": "chaos-daemons",
            "Chaos Knights": "chaos-knights",
            "Chaos Space Marines": "chaos-space-marines",
            "Death Guard": "death-guard",
            "Grey Knights": "grey-knights",
            "Imperial Agents": "imperial-agents",
            "Imperial Knights": "imperial-knights",
            "Space Marines": "space-marines",
            "Thousand Sons": "thousand-sons",
            "World Eaters": "world-eaters",
            "Aeldari": "aeldari",
            "Drukhari": "drukhari",
            "Genestealer Cults": "genestealer-cults",
            "Leagues of Votann": "leagues-of-votann",
            "Necrons": "necrons",
            "Orks": "orks",
            "Tyranids": "tyranids",
            "Unaligned Forces": "unaligned-forces",
            }

    def __init__(self, version_id: str, validate_urls: bool = False):
        """
        Initialize URL configuration.

        Args:
            version_id: Generic version ID (e.g., "10th")
            validate_urls: Whether to validate URLs exist (requires HTTP requests)
        """
        self.version_id = version_id
        self.url_path = self.VERSION_URL_MAPPING.get(
                version_id,
                "wh40k10ed"  # Default to 10th
                )
        self.validate_urls = validate_urls
        self._url_cache = {}  # Cache for constructed URLs

        logger.debug(
                "wahapedia_url_config_initialized",
                version_id=version_id,
                url_path=self.url_path,
                validate_urls=validate_urls
                )

    def get_base_url(self) -> str:
        """Get the base Wahapedia URL."""
        return self.BASE_URL

    def get_version_path(self) -> str:
        """Get the version-specific path component."""
        return self.url_path

    def build_url(self, pattern_name: str, **kwargs) -> Optional[str]:
        """
        Build URL from pattern with parameters.

        Args:
            pattern_name: Name of the URL pattern from URL_PATTERNS
            **kwargs: Parameters to substitute in the pattern

        Returns:
            Constructed URL or None if pattern not found
        """
        if pattern_name not in self.URL_PATTERNS:
            logger.warning(f"Unknown URL pattern: {pattern_name}")
            return None

        # Check cache
        cache_key = f"{pattern_name}:{kwargs}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        pattern = self.URL_PATTERNS[pattern_name]

        # Always add version
        kwargs['version'] = self.url_path

        # Normalize faction code if provided
        if 'faction_code' in kwargs and kwargs['faction_code']:
            kwargs['faction_code'] = self.normalize_faction_code(kwargs['faction_code'])

        # Build the URL
        try:
            # Replace placeholders
            url_path = pattern
            for key, value in kwargs.items():
                placeholder = f"{{{key}}}"
                if placeholder in url_path:
                    url_path = url_path.replace(placeholder, str(value))

            # Check for any remaining placeholders
            if '{' in url_path and '}' in url_path:
                missing = re.findall(r'\{(\w+)\}', url_path)
                logger.warning(f"Missing parameters for {pattern_name}: {missing}")
                return None

            full_url = f"{self.BASE_URL}{url_path}"

            # Cache the result
            self._url_cache[cache_key] = full_url

            return full_url

        except Exception as e:
            logger.error(f"Error building URL for {pattern_name}: {e}")
            return None

    def get_faction_section_url(self, faction_code: str, section: str) -> Optional[str]:
        """
        Get URL for specific section of faction page.

        Args:
            faction_code: Faction code or name
            section: Section name (e.g., 'army_rules', 'detachments')

        Returns:
            Full URL with section anchor
        """
        # Build base faction URL
        base_url = self.build_url('faction_main', faction_code=faction_code)
        if not base_url:
            return None

        # Get section anchor
        anchor = self.SECTION_ANCHORS.get(section)
        if not anchor:
            logger.warning(f"Unknown section: {section}")
            # Try using the section as-is
            anchor = section

        return f"{base_url}#{anchor}"

    def get_quick_start_url(self) -> str:
        """Get URL for quick start guide (has faction dropdown)."""
        return self.build_url('quick_start') or f"{self.BASE_URL}/{self.url_path}/the-rules/quick-start-guide/"

    def get_faction_url(self, faction_code: str) -> str:
        """
        Get URL for a specific faction.

        Args:
            faction_code: Faction code (e.g., "space-marines")

        Returns:
            Full URL to faction page
        """
        return self.build_url('faction_main', faction_code=faction_code) or ""

    def get_faction_datasheets_url(self, faction_code: str) -> str:
        """
        Get URL for faction datasheets.

        Args:
            faction_code: Faction code

        Returns:
            URL to faction datasheets page
        """
        return self.build_url('faction_datasheets', faction_code=faction_code) or ""

    def get_army_lists_url(self) -> str:
        """Get URL for army lists page."""
        return self.build_url('army_lists') or f"{self.BASE_URL}/{self.url_path}/army-lists/"

    def get_unit_datasheet_url(self, faction_code: str, unit_slug: str) -> str:
        """
        Get URL for specific unit datasheet.

        Args:
            faction_code: Faction code
            unit_slug: Unit identifier/slug

        Returns:
            URL to specific unit on datasheets page
        """
        return self.build_url('unit_datasheet', 
                              faction_code=faction_code, 
                              unit_slug=unit_slug) or ""

    def get_search_url(self, query: str) -> str:
        """
        Get search URL with query.

        Args:
            query: Search query string

        Returns:
            Search URL with encoded query
        """
        base_url = self.build_url('search')
        if not base_url:
            base_url = f"{self.BASE_URL}/{self.url_path}/search"

        # Add query parameters
        params = {'q': query}
        return f"{base_url}?{urlencode(params)}"

    def normalize_faction_code(self, faction_input: str) -> str:
        """
        Convert faction name or code to URL-safe code.

        Args:
            faction_input: Faction name or existing code

        Returns:
            Normalized faction code for URLs
        """
        # Check if it's a known faction name
        if faction_input in self.FACTION_CODE_MAPPINGS:
            return self.FACTION_CODE_MAPPINGS[faction_input]

        # Already normalized (check by looking for lowercase and hyphens)
        if faction_input.islower() and '-' in faction_input:
            return faction_input

        # Normalize: lowercase, replace spaces and special chars with hyphens
        normalized = faction_input.lower()

        # Handle special characters
        normalized = normalized.replace("'", "-")
        normalized = normalized.replace("'", "-")  # Handle smart quotes
        normalized = normalized.replace(" ", "-")
        normalized = re.sub(r'[^a-z0-9\-]', '', normalized)
        normalized = re.sub(r'-+', '-', normalized)  # Remove multiple hyphens
        normalized = normalized.strip('-')

        return normalized

    def validate_faction_code(self, faction_code: str) -> bool:
        """
        Validate if faction code is valid.

        Args:
            faction_code: Faction code to validate

        Returns:
            True if valid, False otherwise
        """
        # Check against known mappings
        normalized = self.normalize_faction_code(faction_code)
        valid_codes = set(self.FACTION_CODE_MAPPINGS.values())

        return normalized in valid_codes

    def get_valid_faction_codes(self) -> List[str]:
        """
        Get list of all valid faction codes.

        Returns:
            List of valid faction codes
        """
        return sorted(list(set(self.FACTION_CODE_MAPPINGS.values())))

    def get_urls_for_extractor(self, extractor_name: str) -> List[str]:
        """
        Get URL patterns used by a specific extractor.

        Args:
            extractor_name: Name of the extractor class

        Returns:
            List of URL pattern names
        """
        return self.EXTRACTOR_URL_MAPPING.get(extractor_name, [])

    def get_all_section_anchors(self) -> Dict[str, str]:
        """
        Get all available section anchors.

        Returns:
            Dictionary of section names to anchor values
        """
        return self.SECTION_ANCHORS.copy()

    def build_url_with_anchor(self, pattern_name: str, anchor: str, **kwargs) -> Optional[str]:
        """
        Build URL with an anchor/fragment.

        Args:
            pattern_name: URL pattern name
            anchor: Anchor/fragment to append
            **kwargs: URL parameters

        Returns:
            Full URL with anchor
        """
        base_url = self.build_url(pattern_name, **kwargs)
        if not base_url:
            return None

        # Ensure anchor starts with #
        if not anchor.startswith('#'):
            anchor = f"#{anchor}"

        return f"{base_url}{anchor}"

    def clear_cache(self):
        """Clear the URL cache."""
        self._url_cache.clear()
        logger.debug("URL cache cleared")

    def get_detachments_url(self, faction_code: str) -> str:
        """Get URL for detachments section."""
        return self.get_faction_section_url(faction_code, 'detachments') or ""

    def get_enhancements_url(self, faction_code: str) -> str:
        """Get URL for enhancements section."""
        return self.get_faction_section_url(faction_code, 'enhancements') or ""

    def get_stratagems_url(self, faction_code: str) -> str:
        """Get URL for stratagems."""
        return self.build_url('faction_stratagems', faction_code=faction_code) or ""
