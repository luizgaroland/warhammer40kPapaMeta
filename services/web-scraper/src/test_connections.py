"""
Comprehensive test script for verifying all service connections
"""
import sys
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, '/app')

from src.config import settings
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
    print()
    print("Redis Configuration:")
    print(f"  Host: {settings.redis_host}")
    print(f"  Port: {settings.redis_port}")
    print(f"  Database: {settings.redis_db}")
    
    return True


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
    
    # Test 1: Environment
    try:
        test_environment()
        print_status("Environment variables loaded", True)
    except Exception as e:
        print_status(f"Environment test failed: {e}", False)
        all_tests_passed = False
    
    # Test 2: Database
    print_header("DATABASE CONNECTION TEST")
    try:
        db_success = test_database_connection()
        print_status("Database test complete", db_success)
        if not db_success:
            all_tests_passed = False
    except Exception as e:
        print_status(f"Database test failed: {e}", False)
        all_tests_passed = False
    
    # Test 3: Redis
    print_header("REDIS CONNECTION TEST")
    try:
        redis_success = test_redis_connection()
        print_status("Redis test complete", redis_success)
        if not redis_success:
            all_tests_passed = False
    except Exception as e:
        print_status(f"Redis test failed: {e}", False)
        all_tests_passed = False
    
    # Test 4: Full Integration
    print_header("INTEGRATION TEST")
    try:
        # Publish a test message
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Integration test message"
        }
        
        redis_manager.publish_scraping_status("started", test_data)
        time.sleep(1)
        
        # Check recent messages
        recent = redis_manager.get_recent_messages("scraper:status:started", 1)
        if recent:
            print_status("Integration test passed", True)
            print(f"  Last message: {recent[0].get('details', {}).get('message', 'N/A')}")
        else:
            print_status("Integration test - no messages found", False)
            all_tests_passed = False
            
    except Exception as e:
        print_status(f"Integration test failed: {e}", False)
        all_tests_passed = False
    
    # Final Summary
    print_header("TEST SUMMARY")
    if all_tests_passed:
        print("🎉 All tests passed! Your scraper is ready to run.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        sys.exit(1)
    
    # Cleanup
    db_manager.close()
    redis_manager.close()


if __name__ == "__main__":
    main()
