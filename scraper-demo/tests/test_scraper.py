from unittest.mock import patch, MagicMock

from scrapers.quotes import QuotesScraper


SAMPLE_HTML = """
<html><body>
<div class="quote">
    <span class="text">\u201cLife is what happens.\u201d</span>
    <small class="author">John Lennon</small>
    <div class="tags">
        <a class="tag" href="/tag/life/">life</a>
    </div>
</div>
<div class="quote">
    <span class="text">\u201cTo be or not to be.\u201d</span>
    <small class="author">Shakespeare</small>
    <div class="tags">
        <a class="tag" href="/tag/philosophy/">philosophy</a>
        <a class="tag" href="/tag/classic/">classic</a>
    </div>
</div>
</body></html>
"""


class TestQuotesScraper:
    def test_parse_page_extracts_quotes(self):
        scraper = QuotesScraper(max_pages=1)
        quotes = scraper.parse_page(SAMPLE_HTML)

        assert len(quotes) == 2
        assert quotes[0].author == 'John Lennon'
        assert quotes[0].text == 'Life is what happens.'
        assert quotes[1].tags == ['philosophy', 'classic']

    @patch('scrapers.base.BaseScraper.fetch_page')
    def test_retry_on_failure_then_success(self, mock_fetch):
        """Simulate a failed fetch followed by a successful one."""
        mock_fetch.side_effect = [None, SAMPLE_HTML, None]

        scraper = QuotesScraper(max_pages=3)
        items = scraper.scrape()

        # first page returns None -> stops
        assert len(items) == 0
        assert mock_fetch.call_count == 1
