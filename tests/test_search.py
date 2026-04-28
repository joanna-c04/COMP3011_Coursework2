import unittest
from io import StringIO
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from search import Searcher

# Shared sample index used across all tests
SAMPLE_INDEX = {
  "love": {
    "https://quotes.toscrape.com":         {"frequency": 3, "positions": [0, 5, 10]},
    "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [2]},
  },
  "life": {
    "https://quotes.toscrape.com":         {"frequency": 2, "positions": [1, 6]},
    "https://quotes.toscrape.com/page/3/": {"frequency": 4, "positions": [0, 1, 2, 3]},
  },
  "good": {
    "https://quotes.toscrape.com": {"frequency": 1, "positions": [3]},
  },
}

# Test the print_word method to ensure it correctly displays the index entry for a given word.
class TestPrintWord(unittest.TestCase):
  def setUp(self):
    self.searcher = Searcher(SAMPLE_INDEX)

  def test_prints_existing_word(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("love")
      output = mock_out.getvalue()
    self.assertIn("love", output)

  def test_shows_url(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("love")
      output = mock_out.getvalue()
    self.assertIn("https://quotes.toscrape.com", output)

  def test_shows_frequency(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("love")
      output = mock_out.getvalue()
    self.assertIn("3", output)

  def test_shows_positions(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("love")
      output = mock_out.getvalue()
    self.assertIn("0", output)

  def test_word_not_in_index(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("nonsense")
      output = mock_out.getvalue()
    self.assertIn("not found", output)

  def test_case_insensitive(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("LOVE")
      output = mock_out.getvalue()
    self.assertIn("love", output)

  def test_empty_word_shows_error(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("")
      output = mock_out.getvalue()
    self.assertIn("Error", output)

  def test_whitespace_only_shows_error(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.print_word("   ")
      output = mock_out.getvalue()
    self.assertIn("Error", output)

# Test the find method to ensure it correctly identifies pages containing all query words and ranks them by frequency.
class TestFind(unittest.TestCase):
  def setUp(self):
    self.searcher = Searcher(SAMPLE_INDEX)

  def test_find_single_word_returns_list(self):
    result = self.searcher.find("love")
    self.assertIsInstance(result, list)

  def test_find_single_word_correct_pages(self):
    result = self.searcher.find("love")
    self.assertIn("https://quotes.toscrape.com", result)
    self.assertIn("https://quotes.toscrape.com/page/2/", result)

  def test_find_multi_word_intersection(self):
    # "love" is on page1 and page2, "life" is on page1 and page3
    # intersection = page1 only
    result = self.searcher.find("love life")
    self.assertEqual(result, ["https://quotes.toscrape.com"])

  def test_find_word_not_in_index_returns_empty(self):
    result = self.searcher.find("unicorn")
    self.assertEqual(result, [])

  def test_find_word_not_in_index_prints_message(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.find("unicorn")
      output = mock_out.getvalue()
    # Matches your search.py message: "Words not found in index: unicorn"
    self.assertIn("Words not found in index", output)

  def test_find_empty_query_returns_empty(self):
    result = self.searcher.find("")
    self.assertEqual(result, [])

  def test_find_empty_query_prints_error(self):
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      self.searcher.find("")
      output = mock_out.getvalue()
    self.assertIn("Error", output)

  def test_find_case_insensitive(self):
    result = self.searcher.find("LOVE")
    self.assertIn("https://quotes.toscrape.com", result)

  def test_find_ranked_by_frequency(self):
    # "life" has freq 2 on page1, freq 4 on page3 — page3 should rank first
    result = self.searcher.find("life")
    self.assertEqual(result[0], "https://quotes.toscrape.com/page/3/")

  def test_find_no_pages_in_common_prints_message(self):
    index = {
      "rare": {
        "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [0]}
      },
      "good": {
        "https://quotes.toscrape.com": {"frequency": 1, "positions": [0]}
      }
    }
    searcher = Searcher(index)
    with patch("sys.stdout", new_callable=StringIO) as mock_out:
      result = searcher.find("rare good")
      output = mock_out.getvalue()
    self.assertEqual(result, [])
    self.assertIn("No pages", output)

  def test_find_no_pages_in_common_returns_empty(self):
    index = {
      "rare": {
        "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [0]}
      },
      "good": {
        "https://quotes.toscrape.com": {"frequency": 1, "positions": [0]}
        }
    }
    searcher = Searcher(index)
    result = searcher.find("rare good")
    self.assertEqual(result, [])


if __name__ == "__main__":
  unittest.main()