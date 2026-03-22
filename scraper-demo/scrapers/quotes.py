"""Scraper for quotes.toscrape.com — quotes with pagination and author details."""

import logging
from typing import List, Optional

from bs4 import BeautifulSoup

from models.items import Author, Quote
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class QuotesScraper(BaseScraper):
    """Scrapes quotes, tags, and author details from quotes.toscrape.com."""

    def __init__(self, max_pages: int = 10, delay: float = 1.0, fetch_authors: bool = False) -> None:
        super().__init__(
            base_url="https://quotes.toscrape.com",
            max_pages=max_pages,
            delay=delay,
        )
        self.fetch_authors = fetch_authors
        self._author_cache: dict[str, Author] = {}

    def get_page_url(self, page_number: int) -> str:
        return f"{self.base_url}/page/{page_number}/"

    def parse_page(self, html: str) -> List[Quote]:
        """Extract quotes from a single page.

        Args:
            html: Raw HTML of the quotes page.

        Returns:
            List of Quote objects.
        """
        soup = BeautifulSoup(html, "lxml")
        quotes = []

        for div in soup.select("div.quote"):
            text_el = div.select_one("span.text")
            author_el = div.select_one("small.author")

            if not text_el or not author_el:
                continue

            text = text_el.get_text(strip=True).strip("\u201c\u201d")
            author_name = author_el.get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in div.select("a.tag")]

            author_link = div.select_one("a[href*='/author/']")
            author_url = None
            if author_link and author_link.get("href"):
                author_url = self.base_url + author_link["href"]

            quotes.append(
                Quote(
                    text=text,
                    author=author_name,
                    tags=tags,
                    author_url=author_url,
                )
            )

            if self.fetch_authors and author_url and author_name not in self._author_cache:
                author = self._fetch_author_details(author_url, author_name)
                if author:
                    self._author_cache[author_name] = author

        return quotes

    def _fetch_author_details(self, url: str, name: str) -> Optional[Author]:
        """Fetch detailed author info from their profile page."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")
        born_date_el = soup.select_one("span.author-born-date")
        born_loc_el = soup.select_one("span.author-born-location")
        bio_el = soup.select_one("div.author-description")

        return Author(
            name=name,
            born_date=born_date_el.get_text(strip=True) if born_date_el else None,
            born_location=born_loc_el.get_text(strip=True) if born_loc_el else None,
            bio=bio_el.get_text(strip=True)[:500] if bio_el else None,
        )

    def get_authors(self) -> List[Author]:
        """Return cached author details (only available after scraping with fetch_authors=True)."""
        return list(self._author_cache.values())
