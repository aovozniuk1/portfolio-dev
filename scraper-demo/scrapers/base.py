"""Base scraper with retry logic, rate limiting, and session management."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.helpers import get_random_user_agent

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers.

    Provides session management with automatic retries, rate limiting
    via configurable delays, and User-Agent rotation.
    """

    def __init__(
        self,
        base_url: str,
        max_pages: int = 10,
        delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_pages = max_pages
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout

        self._session = self._build_session()
        self._request_count = 0
        self._start_time: Optional[float] = None

    def _build_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1.0,  # exponential backoff: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self) -> dict:
        """Generate request headers with a rotated User-Agent."""
        return {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with rate limiting and error handling.

        Args:
            url: Full URL to fetch.

        Returns:
            Page HTML content, or None on failure.
        """
        if self._request_count > 0:
            time.sleep(self.delay)

        self._request_count += 1
        logger.debug("Fetching page %d: %s", self._request_count, url)

        try:
            response = self._session.get(
                url, headers=self._get_headers(), timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    @abstractmethod
    def parse_page(self, html: str) -> List[Any]:
        """Parse a single page of HTML and return extracted items.

        Args:
            html: Raw HTML content.

        Returns:
            List of parsed data objects.
        """

    @abstractmethod
    def get_page_url(self, page_number: int) -> str:
        """Build the URL for a given page number.

        Args:
            page_number: 1-based page index.

        Returns:
            Full URL string.
        """

    def scrape(self) -> List[Any]:
        """Run the full scraping pipeline across all pages.

        Returns:
            Aggregated list of all scraped items.
        """
        self._start_time = time.time()
        all_items: List[Any] = []

        logger.info(
            "Starting %s (max %d pages)", self.__class__.__name__, self.max_pages
        )

        for page_num in range(1, self.max_pages + 1):
            url = self.get_page_url(page_num)
            html = self.fetch_page(url)
            if not html:
                logger.warning("Stopping at page %d (fetch failed)", page_num)
                break

            items = self.parse_page(html)
            if not items:
                logger.info("No items found on page %d — finished", page_num)
                break

            all_items.extend(items)
            logger.info("Page %d: scraped %d items (total: %d)", page_num, len(items), len(all_items))

        elapsed = time.time() - self._start_time
        logger.info(
            "Scraping complete: %d items in %.1fs (%d requests)",
            len(all_items),
            elapsed,
            self._request_count,
        )
        return all_items

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
