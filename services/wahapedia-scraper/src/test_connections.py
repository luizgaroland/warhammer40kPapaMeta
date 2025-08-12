#!/usr/bin/env python3
# services/wahapedia-scraper/src/test_connections.py
"""
Comprehensive test script for verifying all service connections
Run this to ensure everything is working before starting scraping
"""
import sys
import time
import json
from datetime import datetime

# Add src to path if needed
sys.path.insert(0, '/app')

from src.config import settings, RedisChannels, MessageTypes
from src.utils.logging import setup_logging, get_logger
from src.database import test_database_connection, db_manager
from src.redis_client import test_redis_connection, redis_manager


def print_header(message: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)


def print_status(message: str, success: bool):
    """Print a status message with emoji"""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


def test_environment():
    """Test environment variables are loaded correctly"""
    print_header("ENVIRONMENT CONFIGURATION")
    
    print(f"Environment: {settings.scraper_env}")
    print(f"Log Level: {settings.log_level}")
    print(f"Wahapedia URL: {settings.wahapedia_base_url}")
    print(f"Rate Limit: {settings.rate_limit_delay} seconds")
    print()
    print("Database Configuration:")
    print(f"  Host: {settings.database_host}")
    print(f"  Port: {settings.database_port}")
    print(f"  Database: {settings.database_name}")
    print(f"  User: {settings.database_user}")
    print(f"  Password: {'*' * len(settings.database_password) if settings.database_password else 'Not Set'}")
    print()
    print("Redis Configuration:")
    print(f"  Host: {settings.redis_host}")
    print(f"  Port: {settings.redis_port}")
    print(f"  Database: {settings.redis_db}")
    print()
    print("Application Paths:")
    print(f"  Log Directory: {settings.log_dir}")
    print(f"  Data Directory: {settings.data_dir}")
    
    return True


def test_logging_system():
    """Test logging configuration"""
    print_header("LOGGING SYSTEM TEST")
    
    try:
        # Test different log levels
        test_logger = get_logger("test")
        
        test_logger.debug("Debug message test")
        test_logger.info("Info message test")
        test_logger.warning("Warning message test")
        test_logger.error("Error message test (this is just a test)")
        
        print_status("Logging system configured", True)
        print_info(f"Logs are being written to {settings.log_dir}")
        
        return True
        
    except Exception as e:
        print_status(f"Logging test failed: {e}", False)
        return False


def test_database_detailed():
    """Run detailed database tests"""
    print_header("DATABASE CONNECTION TEST")
    
    try:
        # Initialize connection
        print("Initializing database connection...")
        if not db_manager.initialize():
            print_status("Database initialization failed", False)
            return False
        
        print_status("Database connection established", True)
        
        # Test basic connectivity
        print("\nTesting database connectivity...")
        if not db_manager.test_connection():
            print_status("Database connectivity test failed", False)
            return False
        
        print_status("Database is responsive", True)
        
        # Verify schema
        print("\nVerifying database schema...")
        schema_results = db_manager.verify_schema()
        
        total_tables = len(schema_results)
        found_tables = sum(1 for v in schema_results.values() if v)
        missing_tables = [k for k, v in schema_results.items() if not v]
        
        print(f"  Tables found: {found_tables}/{total_tables}")
        
        if missing_tables:
            print_status(f"Missing tables detected: {', '.join(missing_tables[:5])}", False)
            print_info("Run 'make init-db' to create the database schema")
            return False
        else:
            print_status("All required tables present", True)
        
        # Test write permissions
        print("\nTesting write permissions...")
        if not db_manager.create_test_entry():
            print_status("Write permission test failed", False)
            return False
        
        print_status("Database write permissions confirmed", True)
        
        # Check current version
        print("\nChecking current game version...")
        version = db_manager.get_current_version()
        if version:
            print_status(f"Current version: {version['major_version']} - {version.get('update_name', 'Base')}", True)
        else:
            print_info("No current version set (this is normal for new installations)")
        
        return True
        
    except Exception as e:
        print_status(f"Database test failed with error: {e}", False)
        return False


def test_redis_detailed():
    """Run detailed Redis tests"""
    print_header("REDIS CONNECTION TEST")
    
    try:
        # Initialize connection
        print("Initializing Redis connection...")
        if not redis_manager.initialize():
            print_status("Redis initialization failed", False)
            return False
        
        print_status("Redis connection established", True)
        
        # Test basic connectivity
        print("\nTesting Redis connectivity...")
        if not redis_manager.test_connection():
            print_status("Redis connectivity test failed", False)
            return False
        
        print_status("Redis is responsive", True)
        
        # Test pub/sub functionality
        print("\nTesting Redis pub/sub system...")
        test_channel = "test:channel"
        test_message = {
            "type": "test",
            "content": "Test message",
            "timestamp": datetime.now().isoformat()
        }
        
        # Create a test subscriber
        received_messages = []
        
        def test_handler(message):
            received_messages.append(message)
            print(f"  Received: {message.get('type', 'unknown')}")
        
        # Subscribe to test channel
        redis_manager.subscribe(test_channel, test_handler)
        time.sleep(0.5)  # Give subscriber time to start
        
        # Publish test message
        redis_manager.publish_message(test_channel, test_message)
        time.sleep(0.5)  # Wait for message to be received
        
        if received_messages:
            print_status("Pub/sub system working", True)
        else:
            print_status("Pub/sub test failed - no messages received", False)
            return False
        
        # Test channel-specific publishers
        print("\nTesting specialized publishers...")
        
        # Test faction publisher
        faction_data = {
            "name": "Test Faction",
            "code": "TEST",
            "detachments": ["Test Detachment"]
        }
        if redis_manager.publish_faction_discovered(faction_data):
            print_status("Faction publisher working", True)
        else:
            print_status("Faction publisher failed", False)
        
        # Test unit publisher
        unit_data = {
            "name": "Test Unit",
            "faction": "TEST",
            "base_points": 100
        }
        if redis_manager.publish_unit_extracted(unit_data):
            print_status("Unit publisher working", True)
        else:
            print_status("Unit publisher failed", False)
        
        # Test status publisher
        if redis_manager.publish_scraping_status("started", {"target": "test"}):
            print_status("Status publisher working", True)
        else:
            print_status("Status publisher failed", False)
        
        return True
        
    except Exception as e:
        print_status(f"Redis test failed with error: {e}", False)
        return False


def test_integration():
    """Test full integration between services"""
    print_header("INTEGRATION TEST")
    
    try:
        print("Testing end-to-end message flow...")
        
        # Create a test scraping session
        test_session = {
            "session_id": f"test_{int(time.time())}",
            "faction": "Test Marines",
            "started_at": datetime.now().isoformat()
        }
        
        # Publish scraping started
        redis_manager.publish_scraping_status("started", test_session)
        print_status("Published scraping start message", True)
        
        # Simulate finding a faction
        faction_message = {
            "name": "Test Marines",
            "code": "TM",
            "detachments": ["Gladius Task Force", "Anvil Siege Force"]
        }
        redis_manager.publish_faction_discovered(faction_message)
        print_status("Published faction discovery", True)
        
        # Simulate extracting units
        units = [
            {"name": "Intercessor Squad", "base_points": 95},
            {"name": "Captain", "base_points": 80},
            {"name": "Redemptor Dreadnought", "base_points": 195}
        ]
        
        for unit in units:
            unit["faction"] = "TM"
            redis_manager.publish_unit_extracted(unit)
        
        print_status(f"Published {len(units)} unit extractions", True)
        
        # Complete scraping
        test_session["completed_at"] = datetime.now().isoformat()
        test_session["units_extracted"] = len(units)
        redis_manager.publish_scraping_status("completed", test_session)
        print_status("Published scraping complete message", True)
        
        # Check if messages were stored
        time.sleep(0.5)
        recent_messages = redis_manager.get_recent_messages(RedisChannels.SCRAPING_COMPLETED, 1)
        
        if recent_messages:
            print_status("Messages successfully stored and retrievable", True)
            latest = recent_messages[0]
            print(f"  Latest message type: {latest.get('type', 'unknown')}")
            print(f"  Units extracted: {latest.get('details', {}).get('units_extracted', 0)}")
        else:
            print_status("Could not retrieve recent messages", False)
            return False
        
        return True
        
    except Exception as e:
        print_status(f"Integration test failed: {e}", False)
        return False


def main():
    """Run all connection tests"""
    print("\n" + "🚀" * 30)
    print(" WAHAPEDIA SCRAPER CONNECTION TEST SUITE")
    print("🚀" * 30)
    
    # Setup logging
    logger = setup_logging(
        log_level=settings.log_level,
        log_dir=settings.log_dir,
        enable_json=False
    )
    
    all_tests_passed = True
    test_results = {}
    
    # Test 1: Environment
    try:
        test_environment()
        print_status("Environment variables loaded", True)
        test_results["environment"] = True
    except Exception as e:
        print_status(f"Environment test failed: {e}", False)
        test_results["environment"] = False
        all_tests_passed = False
    
    # Test 2: Logging
    try:
        if test_logging_system():
            test_results["logging"] = True
        else:
            test_results["logging"] = False
            all_tests_passed = False
    except Exception as e:
        print_status(f"Logging test failed: {e}", False)
        test_results["logging"] = False
        all_tests_passed = False
    
    # Test 3: Database
    try:
        if test_database_detailed():
            test_results["database"] = True
        else:
            test_results["database"] = False
            all_tests_passed = False
    except Exception as e:
        print_status(f"Database test failed: {e}", False)
        test_results["database"] = False
        all_tests_passed = False
    
    # Test 4: Redis
    try:
        if test_redis_detailed():
            test_results["redis"] = True
        else:
            test_results["redis"] = False
            all_tests_passed = False
    except Exception as e:
        print_status(f"Redis test failed: {e}", False)
        test_results["redis"] = False
        all_tests_passed = False
    
    # Test 5: Integration (only if both DB and Redis passed)
    if test_results.get("database") and test_results.get("redis"):
        try:
            if test_integration():
                test_results["integration"] = True
            else:
                test_results["integration"] = False
                all_tests_passed = False
        except Exception as e:
            print_status(f"Integration test failed: {e}", False)
            test_results["integration"] = False
            all_tests_passed = False
    else:
        print_header("INTEGRATION TEST")
        print_info("Skipping integration test due to failed dependencies")
        test_results["integration"] = False
        all_tests_passed = False
    
    # Final Summary
    print_header("TEST SUMMARY")
    print("\nTest Results:")
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name.capitalize():15} {status}")
    
    print()
    if all_tests_passed:
        print("🎉 All tests passed! Your scraper is ready to run.")
        print("\nNext steps:")
        print("  1. Run 'make scrape-faction FACTION=space_marines' to test scraping")
        print("  2. Check logs in /app/logs/wahapedia-scraper.log")
        print("  3. Monitor Redis messages with 'make redis-cli'")
    else:
        print("⚠️  Some tests failed. Please check the output above and:")
        print("  1. Verify your .env file has correct settings")
        print("  2. Ensure all services are running: 'make status'")
        print("  3. Check service logs: 'make logs'")
        
        if not test_results.get("database"):
            print("\n  Database issues:")
            print("    - Run 'make init-db' to create schema")
            print("    - Check PostgreSQL is running: 'docker ps'")
        
        if not test_results.get("redis"):
            print("\n  Redis issues:")
            print("    - Check Redis is running: 'docker ps'")
            print("    - Try 'docker restart warhammer_redis'")
        
        sys.exit(1)
    
    # Cleanup
    print("\nCleaning up connections...")
    db_manager.close()
    redis_manager.close()
    print_status("Cleanup complete", True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
