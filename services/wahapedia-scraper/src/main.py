#!/usr/bin/env python3
"""
Wahapedia Scraper Service - Main Entry Point
"""
import time
import sys
import os

def main():
    print("=" * 50)
    print("Wahapedia Scraper Service Starting...")
    print("=" * 50)
    print(f"Environment: {os.getenv('SCRAPER_ENV', 'development')}")
    print(f"Database Host: {os.getenv('DATABASE_HOST', 'not set')}")
    print(f"Redis Host: {os.getenv('REDIS_HOST', 'not set')}")
    print("=" * 50)
    print("Service is ready and waiting for commands...")
    
    # Keep the container running
    while True:
        time.sleep(60)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scraper service is alive...")

if __name__ == "__main__":
    main()
