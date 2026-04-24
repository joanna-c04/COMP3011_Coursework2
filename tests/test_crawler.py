import unittest
from unittest.mock import patch, MagicMock, mock_open
from bs4 import BeautifulSoup
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from crawler import Crawler

def make_mock_response(html):
  mock = MagicMock()
  mock.text = html
  mock.raise_for_status = MagicMock()
  
  return mock

# Test the _is_valid_url method to ensure it correctly identifies valid and invalid URLs.
class TestIsValidUrl(unittest.TestCase):
  def setUp(self):
    self.crawler = Crawler("https://quotes.toscrape.com")
  
  def test_same_domain_accepted(self):
    self.assertTrue(
      self.crawler._is_valid_url("https://quotes.toscrape.com/page/2/")
    )
  
  def test_external_domain_rejected(self):
    self.assertFalse(
      self.crawler._is_valid_url("https://example.com")
    )
  
  def test_ftp_scheme_rejected(self):
    self.assertFalse(
      self.crawler._is_valid_url("ftp://quotes.toscrape.com")
    )

  def test_empty_string_rejected(self):
    self.assertFalse(
      self.crawler._is_valid_url("")
    )

  def test_subdomain_rejected(self):
    self.assertFalse(
      self.crawler._is_valid_url("https://sub.quotes.toscrape.com")
    )

# Test the _extract_text method to ensure it correctly extracts quotes and authors from the HTML.
class TestExtractText(unittest.TestCase):
  def setUp(self):
    self.crawler = Crawler("https://quotes.toscrape.com")
  
  def _soup(self, html):
    return BeautifulSoup(html, "html.parser")
  
  def test_extracts_quote_and_author(self):
    html = """
    <div class="quote">
      <span class="text">“Example quote.”</span>
      <small class="author">Example Author</small>
    </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertIn("“Example quote.”", text)
    self.assertIn("Example Author", text)

  def test_quote_and_author_joined_with_by(self):
    html = """
    <div class="quote">
      <span class="text">“Another quote.”</span>
      <small class="author">Another Author</small>
    </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertIn("“Another quote.” by Another Author", text)

  def test_multiple_quotes_extracted(self):
    html = """
    <div class="quote">
      <span class="text">“First quote.”</span>
      <small class="author">First Author</small>
    </div>
    <div class="quote">
      <span class="text">“Second quote.”</span>
      <small class="author">Second Author</small>
    </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertIn("“First quote.” by First Author", text)
    self.assertIn("“Second quote.” by Second Author", text)

  def test_ignores_nagivation_text(self):
    html = """
      <nav>Login Top Tags</nav>
      <div class="quote">
        <span class="text">"Only this."</span>
        <small class="author">Someone</small>
      </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertNotIn("Loging", text)
    self.assertNotIn("Top Tags", text)

  def test_no_quotes_returns_empty_string(self):
    html = "<html><body><p>No quotes here</p></body></html>"
    text = self.crawler._extract_text(self._soup(html))
    self.assertEqual(text, "")

  def test_quote_missing_author_skipped(self):
    html = """
    <div class="quote">
      <span class="text">“Quote without author.”</span>
    </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertEqual(text, "")

  def test_tags_not_included_in_output(self):
    html = """
      <div class="quote">
        <span class="text">"A quote."</span>
        <small class="author">Someone</small>
        <div class="tags">love humor</div>
      </div>
    """
    text = self.crawler._extract_text(self._soup(html))
    self.assertNotIn("love", text)
    self.assertNotIn("humor", text)

# Test the _extract_links method to ensure it correctly identifies the next page link.
class TestExtractLinks(unittest.TestCase):
  def setUp(self):
    self.crawler = Crawler("https://quotes.toscrape.com")
    self.base = "https://quotes.toscrape.com"
  
  def _soup(self, html):
    return BeautifulSoup(html, "html.parser")
  
  def test_returns_next_page_url(self):
    html = '<li class="next"><a href="/page/2/">Next</a></li>'
    result = self.crawler._extract_links(self._soup(html), self.base)
    self.assertEqual(result, "https://quotes.toscrape.com/page/2/")

  def test_returns_none_when_no_next_button(self):
    html = "<li class='previous'><a href='/page/1/'>Previous</a></li>"
    result = self.crawler._extract_links(self._soup(html), self.base)
    self.assertIsNone(result)

  def test_returns_none_on_last_page(self):
    html = "<p>No navigation here</p>"
    result = self.crawler._extract_links(self._soup(html), self.base)
    self.assertIsNone(result)

  def test_relative_url_resolved_to_absolute(self):
    html = '<li class="next"><a href="/page/3/">Next</a></li>'
    result = self.crawler._extract_links(self._soup(html), self.base)
    self.assertTrue(result.startswith("https://"))

  def test_external_next_url_rejected(self):
    html = '<li class="next"><a href="https://example.com/next">Next</a></li>'
    result = self.crawler._extract_links(self._soup(html), self.base)
    self.assertIsNone(result)

# Test the crawl method to ensure it correctly fetches pages and extracts content.
class TestCrawl(unittest.TestCase):
  def setUp(self):
    self.crawler = Crawler("https://quotes.toscrape.com", politeness_window=0)
  
  def _make_page(self, quote, author, has_next = True, next_page = "/page/2/"):
    """Helper to build a realistic quotes page HTML."""
    next_html = f'<li class="next"><a href="{next_page}">Next</a></li>' if has_next else ""
    return f"""
    <html><body>
      <div class="quote">
        <span class="text">"{quote}"</span>
        <small class="author">{author}</small>
      </div>
      <ul class="pager">{next_html}</ul>
    </body></html>
    """ 

  @patch("crawler.requests.get")
  def test_crawl_returns_dict(self, mock_get):
    mock_get.return_value = make_mock_response(self._make_page("A quote", "An author", has_next = False))
    pages = self.crawler.crawl()
    self.assertIsInstance(pages, dict)

  @patch("crawler.requests.get")
  def test_base_url_in_pages(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("A quote", "An author", has_next = False)
    )
    pages = self.crawler.crawl()
    self.assertIn("https://quotes.toscrape.com", pages)

  @patch("crawler.requests.get")
  def test_follows_next_page(self, mock_get):
    page1 = make_mock_response(self._make_page("Quote 1", "Author 1", has_next = True))
    page2 = make_mock_response(self._make_page("Quote 2", "Author 2", has_next = False))
    mock_get.side_effect = [page1, page2]
    pages = self.crawler.crawl()
    self.assertEqual(len(pages), 2)

  @patch("crawler.requests.get")
  def test_stops_at_last_page(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("Quote", "Author", has_next = False)
    )
    pages = self.crawler.crawl()
    # Only 1 page fetched, then stopped
    self.assertEqual(mock_get.call_count, 1)
 
  @patch("crawler.requests.get")
  def test_does_not_revisit_pages(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("Quote", "Author", has_next = False)
    )
    self.crawler.crawl()
    self.assertEqual(mock_get.call_count, 1)

  @patch("crawler.requests.get")
  def test_network_error_handled_gracefully(self, mock_get):
    import requests as req
    mock_get.side_effect = req.RequestException("timeout")
    pages = self.crawler.crawl()
    self.assertEqual(pages, {})

  @patch("crawler.requests.get")
  def test_page_text_contains_quote_and_author(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("Life is good", "Albert Einstein", has_next = False)
    )
    pages = self.crawler.crawl()
    text = pages["https://quotes.toscrape.com"]
    self.assertIn("Life is good", text)
    self.assertIn("Albert Einstein", text)
 
  @patch("crawler.requests.get")
  def test_saves_to_file_when_save_path_given(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("A quote", "An Author", has_next = False)
    )
    with tempfile.NamedTemporaryFile(suffix=".json", delete = False) as f:
      path = f.name
    try:
      self.crawler.crawl(save_path = path)
      with open(path, encoding = "utf-8") as f:
          data = json.load(f)
      self.assertIsInstance(data, dict)
      self.assertIn("https://quotes.toscrape.com", data)
    finally:
      os.remove(path)

  @patch("crawler.requests.get")
  def test_no_file_saved_without_save_path(self, mock_get):
    mock_get.return_value = make_mock_response(
      self._make_page("A quote", "An Author", has_next = False)
    )
    # Should complete without any file IO errors
    pages = self.crawler.crawl(save_path = None)
    self.assertEqual(len(pages), 1)
 
 
if __name__ == "__main__":
  unittest.main()
 