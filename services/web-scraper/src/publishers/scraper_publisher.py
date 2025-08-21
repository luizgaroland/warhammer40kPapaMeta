# services/web-scraper/src/publishers/scraper_publisher.py

import sys
sys.path.insert(0, '/app/src')

import json
from typing import Dict, List, Any
from datetime import datetime
from redis_client import redis_manager  # Use the existing redis_manager
import logging

class ScraperPublisher:
    """Publisher for scraped Wahapedia data to Redis channels."""

    # Channel names for different data types
    CHANNELS = {
            'factions': 'wahapedia:factions',
            'army_rules': 'wahapedia:army_rules',
            'detachments': 'wahapedia:detachments',
            'enhancements': 'wahapedia:enhancements',
            'units': 'wahapedia:units',
            'wargear': 'wahapedia:wargear',
            'scraping_status': 'wahapedia:status',
            }

    def __init__(self):
        """Initialize the publisher with Redis connection."""
        # Initialize Redis if not already done
        if not redis_manager.is_connected:
            redis_manager.initialize()

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def publish_factions(self, factions: List[Dict[str, str]]) -> bool:
        """
        Publish faction list to Redis.

        Args:
            factions: List of faction dictionaries

        Returns:
            True if successful, False otherwise
        """
        try:
            message = {
                    'type': 'faction_list',
                    'count': len(factions),
                    'data': factions,
                    'timestamp': datetime.now().isoformat()
                    }

            # Use redis_manager's publish_message method
            success = redis_manager.publish_message(
                    self.CHANNELS['factions'], 
                    message
                    )

            if success:
                self.logger.info(
                        f"Published {len(factions)} factions to {self.CHANNELS['factions']}"
                        )
                # Also store in Redis for persistence
                self._store_factions(factions)

            return success

        except Exception as e:
            self.logger.error(f"Error publishing factions: {str(e)}")
            return False

    def _store_factions(self, factions: List[Dict[str, str]]):
        """
        Store factions in Redis for persistence.

        Args:
            factions: List of faction dictionaries
        """
        try:
            client = redis_manager.client
            pipe = client.pipeline()

            # Clear old data
            pipe.delete('wahapedia:faction_list')
            pipe.delete('wahapedia:faction_codes')

            # Store each faction
            for faction in factions:
                # Store in hash by code for quick lookup
                pipe.hset(
                        'wahapedia:faction_codes',
                        faction['code'],
                        json.dumps(faction)
                        )

                # Store in list for iteration
                pipe.rpush('wahapedia:faction_list', json.dumps(faction))

            # Set expiry (24 hours)
            pipe.expire('wahapedia:faction_codes', 86400)
            pipe.expire('wahapedia:faction_list', 86400)

            pipe.execute()
            self.logger.info(f"Stored {len(factions)} factions in Redis")

        except Exception as e:
            self.logger.error(f"Error storing factions: {str(e)}")

    def publish_status(self, status: str, details: Dict[str, Any] = None):
        """
        Publish scraping status updates.

        Args:
            status: Status message (e.g., 'started', 'completed', 'error')
            details: Additional details about the status
        """
        try:
            message = {
                    'status': status,
                    'details': details or {},
                    'timestamp': datetime.now().isoformat()
                    }

            redis_manager.publish_message(
                    self.CHANNELS['scraping_status'],
                    message
                    )

            self.logger.info(f"Published status: {status}")

        except Exception as e:
            self.logger.error(f"Error publishing status: {str(e)}")
