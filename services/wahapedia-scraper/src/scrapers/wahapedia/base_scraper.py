# services/wahapedia-scraper/src/scrapers/wahapedia/base_scraper.py

import time
import random
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import sys
import os

# Add the src directory to Python path
# When running in Docker, we're at /app, so src is at /app/src
sys.path.insert(0, '/app/src')

# Now we can import from utils
from utils.logging import get_logger

class BaseScraper:
    """Base scraper class with rate limiting, session management, and error handling."""

    BASE_URL = "https://wahapedia.ru"

    def __init__(self, rate_limit_min: float = 2.0, rate_limit_max: float = 3.0):
        """
        Initialize the base scraper with session and rate limiting.

        Args:
            rate_limit_min: Minimum seconds between requests
            rate_limit_max: Maximum seconds between requests
        """
        self.logger = get_logger(self.__class__.__name__)
        self.rate_limit_min = rate_limit_min
        self.rate_limit_max = rate_limit_max
        self.last_request_time = 0

        # Create session with retry strategy
        self.session = self._create_session()

        # Set a user agent to identify our bot
        self.session.headers.update({
            'User-Agent': 'Warhammer40kMetaAnalysis/1.0 (Educational Project; Respectful Scraping)'
            })

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
                )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # Calculate random delay between min and max
        delay = random.uniform(self.rate_limit_min, self.rate_limit_max)

        if time_since_last_request < delay:
            sleep_time = delay - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_page(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch a page with rate limiting and error handling.

        Args:
            url: URL to fetch (can be relative or absolute)
            timeout: Request timeout in seconds

        Returns:
            HTML content as string, or None if failed
        """
        # Convert relative URLs to absolute
        if not url.startswith('http'):
            url = f"{self.BASE_URL}{url}"

        # Apply rate limiting
        self._rate_limit()

        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            self.logger.debug(f"Successfully fetched {len(response.content)} bytes")
            return response.text

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content into BeautifulSoup object.

        Args:
            html: HTML content as string

        Returns:
            BeautifulSoup object, or None if parsing failed
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
            return None

    def fetch_and_parse(self, url: str) -> Optional[BeautifulSoup]:
        """
        Convenience method to fetch and parse in one step.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object, or None if failed
        """
        html = self.fetch_page(url)
        if html:
            return self.parse_html(html)
        return None

    def safe_extract_text(self, element, default: str = "") -> str:
        """
        Safely extract text from a BeautifulSoup element.

        Args:
            element: BeautifulSoup element
            default: Default value if element is None

        Returns:
            Extracted text or default value
        """
        if element:
            return element.get_text(strip=True)
        return default

    def safe_extract_attribute(self, element, attribute: str, default: str = "") -> str:
        """
        Safely extract an attribute from a BeautifulSoup element.

        Args:
            element: BeautifulSoup element
            attribute: Attribute name to extract
            default: Default value if element or attribute is None

        Returns:
            Attribute value or default
        """
        if element:
            return element.get(attribute, default)
        return default

    def simulate_hover(self, soup: BeautifulSoup, element_selector: str) -> bool:
        """
        Simulate hover effect for dropdown menus.
        Note: Wahapedia's dropdowns are CSS-based, so we just need to find
        the dropdown content that's normally hidden.

        Args:
            soup: BeautifulSoup object
            element_selector: CSS selector for the element to "hover"

        Returns:
            True if hover element found, False otherwise
        """
        hover_element = soup.select_one(element_selector)
        if hover_element:
            self.logger.debug(f"Found hover element: {element_selector}")
            return True
        return False
