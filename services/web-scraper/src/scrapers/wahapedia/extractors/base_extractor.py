# services/web-scraper/src/scrapers/wahapedia/extractors/base_extractor.py

from typing import Optional, Dict, Any, List
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from services.wahapedia.url_config import WahapediaURLConfig
from scrapers.wahapedia.base_scraper import BaseScraper
from publishers.scraper_publisher import ScraperPublisher

class BaseExtractor(BaseScraper):
    """Base extractor with URL configuration support and standardized functionality."""

    def __init__(self, version_id: str = "10th", publish_to_redis: bool = True, rate_limit_min: float = 2.0, rate_limit_max: float = 3.0):
        """
        Initialize the base extractor.
        
        Args:
            version_id: Warhammer 40k edition version (default: "10th")
            publish_to_redis: Whether to publish results to Redis
            rate_limit_min: Minimum seconds between requests
            rate_limit_max: Maximum seconds between requests
        """
        super().__init__(rate_limit_min=rate_limit_min, rate_limit_max=rate_limit_max)
        self.url_config = WahapediaURLConfig(version_id)
        self.publish_to_redis = publish_to_redis
        self.version_id = version_id
        self.extracted_data = []
        
        # Initialize publisher if Redis is enabled
        if self.publish_to_redis:
            self.publisher = ScraperPublisher()

    def get_url_for_faction(self, faction_code: str) -> str:
        """Get versioned URL for faction."""
        return self.url_config.get_faction_url(faction_code)

    def validate_faction_data(self, faction_data: Dict[str, str]) -> bool:
        """
        Validate faction data structure.
        
        Args:
            faction_data: Dictionary containing faction information
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['name', 'url', 'code']
        return all(field in faction_data and faction_data[field] for field in required_fields)

    def safe_extract_faction_info(self, faction_data: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Safely extract faction information with validation.
        
        Args:
            faction_data: Dictionary containing faction information
            
        Returns:
            Validated faction data or None if invalid
        """
        if not self.validate_faction_data(faction_data):
            self.logger.error(f"Invalid faction data: {faction_data}")
            return None
        return faction_data

    def publish_status(self, status: str, data: Dict[str, Any]) -> bool:
        """
        Publish status update to Redis if enabled.
        
        Args:
            status: Status type ('started', 'completed', 'error')
            data: Additional data to include
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.publish_to_redis:
            return True
            
        try:
            self.publisher.publish_status(status, data)
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish status: {str(e)}")
            return False

    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """
        Save extracted data to JSON file.
        
        Args:
            data: Data to save
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not data:
            self.logger.warning("No data to save")
            return False

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Saved {len(data)} items to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return False

    def get_extraction_summary(self) -> Dict[str, Any]:
        """
        Get summary of extraction results.
        
        Returns:
            Dictionary with extraction summary
        """
        return {
            'extractor_type': self.__class__.__name__,
            'version_id': self.version_id,
            'total_extracted': len(self.extracted_data),
            'publish_to_redis': self.publish_to_redis
        }
