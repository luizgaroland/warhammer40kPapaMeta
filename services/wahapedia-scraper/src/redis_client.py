# services/wahapedia-scraper/src/redis_client.py
"""
Redis connection and pub/sub management for Wahapedia Scraper
"""
import json
import time
import threading
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime

import redis
from redis.exceptions import ConnectionError, TimeoutError

from src.config import settings, RedisChannels, MessageTypes
from src.utils.logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """Manages Redis connections and pub/sub operations"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscriber_thread: Optional[threading.Thread] = None
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.is_connected = False
        
    def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            # Create Redis client
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.client.ping()
            self.is_connected = True
            
            # Get Redis info
            info = self.client.info()
            logger.info(
                "redis_connected",
                redis_version=info.get('redis_version'),
                used_memory=info.get('used_memory_human'),
                connected_clients=info.get('connected_clients')
            )
            
            return True
            
        except (ConnectionError, TimeoutError) as e:
            logger.error("redis_connection_failed", error=str(e))
            self.is_connected = False
            return False
    
    def test_connection(self) -> bool:
        """Test Redis connectivity"""
        try:
            if not self.client:
                return False
            response = self.client.ping()
            return response == True
        except Exception as e:
            logger.error("redis_test_failed", error=str(e))
            return False
    
    def publish_message(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to a Redis channel
        
        Args:
            channel: Channel name to publish to
            message: Message dictionary to publish
            
        Returns:
            Success status
        """
        try:
            if not self.client:
                raise RuntimeError("Redis not initialized")
            
            # Add metadata to message
            message['timestamp'] = datetime.now().isoformat()
            message['source'] = 'wahapedia-scraper'
            
            # Serialize and publish
            message_json = json.dumps(message)
            subscribers = self.client.publish(channel, message_json)
            
            logger.debug(
                "message_published",
                channel=channel,
                message_type=message.get('type'),
                subscribers=subscribers
            )
            
            # Also save to redis_messages table tracking
            self._track_message(channel, message)
            
            return True
            
        except Exception as e:
            logger.error(
                "publish_failed",
                channel=channel,
                error=str(e)
            )
            return False
    
    def _track_message(self, channel: str, message: Dict[str, Any]):
        """Track published message in Redis for monitoring"""
        try:
            # Store recent messages in a Redis list for debugging
            key = f"messages:{channel}:recent"
            self.client.lpush(key, json.dumps(message))
            self.client.ltrim(key, 0, 99)  # Keep only last 100 messages
            self.client.expire(key, 3600)  # Expire after 1 hour
        except Exception as e:
            logger.debug("message_tracking_failed", error=str(e))
    
    def subscribe(self, channel: str, handler: Callable[[Dict], None]):
        """
        Subscribe to a Redis channel with a message handler
        
        Args:
            channel: Channel to subscribe to
            handler: Function to call when message received
        """
        if channel not in self.message_handlers:
            self.message_handlers[channel] = []
        self.message_handlers[channel].append(handler)
        
        # Start subscriber thread if not running
        if not self.subscriber_thread or not self.subscriber_thread.is_alive():
            self._start_subscriber()
    
    def _start_subscriber(self):
        """Start the subscriber thread"""
        if not self.client:
            raise RuntimeError("Redis not initialized")
        
        self.pubsub = self.client.pubsub()
        
        # Subscribe to all channels with handlers
        for channel in self.message_handlers.keys():
            self.pubsub.subscribe(channel)
            logger.info("subscribed_to_channel", channel=channel)
        
        # Start listener thread
        self.subscriber_thread = threading.Thread(
            target=self._listen_for_messages,
            daemon=True
        )
        self.subscriber_thread.start()
    
    def _listen_for_messages(self):
        """Listen for messages on subscribed channels"""
        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    # Call handlers for this channel
                    if channel in self.message_handlers:
                        for handler in self.message_handlers[channel]:
                            try:
                                handler(data)
                            except Exception as e:
                                logger.error(
                                    "message_handler_error",
                                    channel=channel,
                                    error=str(e)
                                )
        except Exception as e:
            logger.error("subscriber_thread_error", error=str(e))
    
    def test_pubsub(self) -> bool:
        """Test Redis pub/sub functionality"""
        test_channel = "test:pubsub"
        test_message = {
            "type": "test",
            "message": "Testing Redis pub/sub",
            "timestamp": datetime.now().isoformat()
        }
        
        received = []
        
        def test_handler(message):
            received.append(message)
            logger.debug("test_message_received", message=message)
        
        try:
            # Subscribe to test channel
            self.subscribe(test_channel, test_handler)
            
            # Give subscriber time to start
            time.sleep(0.5)
            
            # Publish test message
            self.publish_message(test_channel, test_message)
            
            # Wait for message to be received
            time.sleep(0.5)
            
            # Check if message was received
            success = len(received) > 0
            
            if success:
                logger.info("✓ Redis pub/sub test successful")
            else:
                logger.warning("Redis pub/sub test failed - no messages received")
            
            return success
            
        except Exception as e:
            logger.error("redis_pubsub_test_failed", error=str(e))
            return False
    
    def publish_faction_discovered(self, faction_data: Dict[str, Any]):
        """Publish faction discovered message"""
        message = {
            "type": MessageTypes.FACTION_DISCOVERED,
            "version": "10th",
            "data": faction_data
        }
        return self.publish_message(RedisChannels.FACTION_DISCOVERED, message)
    
    def publish_unit_extracted(self, unit_data: Dict[str, Any]):
        """Publish unit extracted message"""
        message = {
            "type": MessageTypes.UNIT_EXTRACTED,
            "version": "10th",
            "data": unit_data
        }
        return self.publish_message(RedisChannels.UNIT_EXTRACTED, message)
    
    def publish_scraping_status(self, status: str, details: Dict[str, Any] = None):
        """Publish scraping status update"""
        message = {
            "type": MessageTypes.STATUS_UPDATE,
            "status": status,
            "details": details or {}
        }
        
        channel_map = {
            "started": RedisChannels.SCRAPING_STARTED,
            "completed": RedisChannels.SCRAPING_COMPLETED,
            "failed": RedisChannels.SCRAPING_FAILED
        }
        
        channel = channel_map.get(status, RedisChannels.SCRAPING_STARTED)
        return self.publish_message(channel, message)
    
    def get_recent_messages(self, channel: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from a channel (for debugging)"""
        try:
            key = f"messages:{channel}:recent"
            messages = self.client.lrange(key, 0, limit - 1)
            return [json.loads(msg) for msg in messages]
        except Exception as e:
            logger.error("get_recent_messages_failed", error=str(e))
            return []
    
    def close(self):
        """Close Redis connections"""
        if self.pubsub:
            self.pubsub.close()
        if self.client:
            self.client.close()
        self.is_connected = False
        logger.info("redis_connections_closed")


# Global Redis manager instance
redis_manager = RedisManager()


def init_redis() -> bool:
    """Initialize Redis connection"""
    return redis_manager.initialize()


def test_redis_connection():
    """Test Redis connectivity and pub/sub"""
    logger.info("Testing Redis connection...")
    
    # Initialize connection
    if not redis_manager.initialize():
        logger.error("Failed to initialize Redis connection")
        return False
    
    # Test basic connectivity
    if not redis_manager.test_connection():
        logger.error("Redis connection test failed")
        return False
    
    logger.info("✓ Redis connection successful")
    
    # Test pub/sub
    if not redis_manager.test_pubsub():
        logger.error("Redis pub/sub test failed")
        return False
    
    logger.info("✓ Redis pub/sub working")
    
    return True
