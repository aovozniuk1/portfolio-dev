"""Scraper for books.toscrape.com — books with categories, prices, and ratings."""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models.items import Book
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


class BooksScraper(BaseScraper):
    """Scrapes book listings from books.toscrape.com with optional detail pages."""

    def __init__(
        self,
        max_pages: int = 10,
        delay: float = 1.0,
        category: Optional[str] = None,
        fetch_details: bool = False,
    ) -> None:
        super().__init__(
            base_url="https://books.toscrape.com",
            max_pages=max_pages,
            delay=delay,
        )
        self.category = category
        self.fetch_details = fetch_details
        self._category_url: Optional[str] = None

    def get_page_url(self, page_number: int) -> str:
        if self._category_url:
            if page_number == 1:
                return self._category_url
            base = self._category_url.rsplit("/", 1)[0]
            return f"{base}/page-{page_number}.html"
        if page_number == 1:
            return f"{self.base_url}/catalogue/page-1.html"
        return f"{self.base_url}/catalogue/page-{page_number}.html"

    def _resolve_category(self) -> None:
        if not self.category:
            return

        html = self.fetch_page(self.base_url)
        if not html:
            return

        soup = BeautifulSoup(html, "lxml")
        for link in soup.select("ul.nav-list ul a"):
            name = link.get_text(strip=True).lower()
            if name == self.category.lower():
                self._category_url = urljoin(self.base_url + "/", link["href"])
                logger.info("Resolved category '%s' -> %s", self.category, self._category_url)
                return

        logger.warning("Category '%s' not found, scraping all books", self.category)

    def scrape(self) -> List[Book]:
        """Resolve category if needed, then run the standard scrape loop."""
        if self.category:
            self._resolve_category()
        return super().scrape()

    def parse_page(self, html: str) -> List[Book]:
        """Extract books from a catalogue listing page.

        Args:
            html: Raw HTML of the listing page.

        Returns:
            List of Book objects.
        """
        soup = BeautifulSoup(html, "lxml")
        books = []

        for article in soup.select("article.product_pod"):
            title_el = article.select_one("h3 a")
            price_el = article.select_one("p.price_color")
            avail_el = article.select_one("p.instock")
            rating_el = article.select_one("p.star-rating")

            if not title_el or not price_el:
                continue

            title = title_el.get("title", title_el.get_text(strip=True))
            price = self._parse_price(price_el.get_text(strip=True))
            availability = avail_el.get_text(strip=True) if avail_el else "Unknown"
            rating = self._parse_rating(rating_el)

            book = Book(
                title=title,
                price=price,
                rating=rating,
                availability=availability,
                category=self.category or "all",
            )

            if self.fetch_details and title_el.get("href"):
                detail_url = urljoin(self.base_url + "/catalogue/", title_el["href"])
                self._enrich_book(book, detail_url)

            books.append(book)

        return books

    def _enrich_book(self, book: Book, url: str) -> None:
        html = self.fetch_page(url)
        if not html:
            return

        soup = BeautifulSoup(html, "lxml")

        table = soup.select_one("table.table-striped")
        if table:
            rows = {
                row.select_one("th").get_text(strip=True): row.select_one("td").get_text(strip=True)
                for row in table.select("tr")
                if row.select_one("th") and row.select_one("td")
            }
            book.upc = rows.get("UPC")

        desc_el = soup.select_one("#product_description ~ p")
        if desc_el:
            book.description = desc_el.get_text(strip=True)[:500]

        img_el = soup.select_one("#product_gallery img")
        if img_el and img_el.get("src"):
            book.image_url = urljoin(self.base_url + "/", img_el["src"])

    @staticmethod
    def _parse_price(price_str: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", price_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_rating(element) -> int:
        if not element:
            return 0
        classes = element.get("class", [])
        for cls in classes:
            if cls.lower() in RATING_MAP:
                return RATING_MAP[cls.lower()]
        return 0
