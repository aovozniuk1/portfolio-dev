"""Data models for scraped items."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Author:
    """Author information from quotes.toscrape.com."""

    name: str
    born_date: Optional[str] = None
    born_location: Optional[str] = None
    bio: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Quote:
    """A single quote with metadata."""

    text: str
    author: str
    tags: List[str] = field(default_factory=list)
    author_url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Book:
    """Book information from books.toscrape.com."""

    title: str
    price: float
    rating: int
    availability: str
    category: str
    upc: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
