# services/wahapedia-scraper/tests/test_redis_subscriber.py

import sys
sys.path.insert(0, '/app/src')

import json
import signal
from redis_client import redis_manager  # Use the existing redis_manager

class TestSubscriber:
    """Test subscriber to verify Redis messages are being published correctly."""

    def __init__(self):
        # Initialize Redis if not already done
        if not redis_manager.is_connected:
            redis_manager.initialize()

        self.running = True

    def handle_message(self, message_data):
        """Handle incoming Redis message."""
        try:
            print(f"\n{'='*60}")
            print(f"Message Type: {message_data.get('type', 'unknown')}")

            if 'status' in message_data:
                print(f"Status: {message_data['status']}")
                if 'details' in message_data:
                    print(f"Details: {message_data['details']}")

            if 'count' in message_data:
                print(f"Count: {message_data['count']}")

            if 'data' in message_data and isinstance(message_data['data'], list):
                print(f"Sample data (first 3 items):")
                for item in message_data['data'][:3]:
                    print(f"  - {item.get('name', 'Unknown')}: {item.get('code', 'N/A')}")

            print(f"Timestamp: {message_data.get('timestamp', 'N/A')}")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error handling message: {e}")

    def subscribe_and_listen(self):
        """Subscribe to channels and listen for messages."""
        # Subscribe to all wahapedia channels
        channels = [
                'wahapedia:factions',
                'wahapedia:status',
                'wahapedia:army_rules',
                'wahapedia:detachments',
                'wahapedia:enhancements',
                'wahapedia:units',
                ]

        print(f"Subscribing to channels: {', '.join(channels)}")

        # Subscribe to each channel with our handler
        for channel in channels:
            redis_manager.subscribe(channel, self.handle_message)

        print("\nListening for messages... (Press Ctrl+C to stop)\n")

        # Set up signal handler for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

        # Keep the main thread alive
        import time
        while self.running:
            time.sleep(1)

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\nShutting down subscriber...")
        sel
