import unittest
import json
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from indexer import Indexer

# Test the _tokenise method.
class TestTokenise(unittest.TestCase):
  def setUp(self):
    self.indexer = Indexer()

  def test_basic_tokenisation(self):
    tokens = self.indexer._tokenise("Hello world")
    self.assertEqual(tokens, ["hello", "world"])

  def test_lowercases_words(self):
    tokens = self.indexer._tokenise("Good GOOD good")
    self.assertEqual(tokens, ["good", "good", "good"])

  def test_strips_punctuation(self):
    tokens = self.indexer._tokenise("Hello, world!")
    self.assertIn("hello", tokens)
    self.assertIn("world", tokens)

  def test_strips_curly_quotes(self):
    tokens = self.indexer._tokenise("\u201cHello\u201d")
    self.assertIn("hello", tokens)

  def test_empty_string_returns_empty_list(self):
    tokens = self.indexer._tokenise("")
    self.assertEqual(tokens, [])

  def test_numbers_excluded(self):
    tokens = self.indexer._tokenise("page 42 results")
    self.assertNotIn("42", tokens)

  def test_multiple_spaces_handled(self):
    tokens = self.indexer._tokenise("one   two   three")
    self.assertEqual(tokens, ["one", "two", "three"])

# Test the add_page method to ensure it correctly updates the index with word frequencies and positions.
class TestAddPage(unittest.TestCase):
  def setUp(self):
    self.indexer = Indexer()
    self.url = "https://quotes.toscrape.com"

  def test_word_added_to_index(self):
    self.indexer.add_page(self.url, "hello world")
    self.assertIn("hello", self.indexer.index)

  def test_url_added_under_word(self):
    self.indexer.add_page(self.url, "hello world")
    self.assertIn(self.url, self.indexer.index["hello"])

  def test_frequency_correct(self):
    self.indexer.add_page(self.url, "good good bad")
    self.assertEqual(self.indexer.index["good"][self.url]["frequency"], 2)

  def test_positions_correct(self):
    self.indexer.add_page(self.url, "one two one")
    positions = self.indexer.index["one"][self.url]["positions"]
    self.assertEqual(positions, [0, 2])

  def test_case_insensitive(self):
    self.indexer.add_page(self.url, "Good GOOD good")
    freq = self.indexer.index["good"][self.url]["frequency"]
    self.assertEqual(freq, 3)

  def test_multiple_pages_same_word(self):
    url2 = "https://quotes.toscrape.com/page/2/"
    self.indexer.add_page(self.url, "hello world")
    self.indexer.add_page(url2, "hello there")
    self.assertIn(self.url, self.indexer.index["hello"])
    self.assertIn(url2, self.indexer.index["hello"])

  def test_empty_text_does_not_crash(self):
    self.indexer.add_page(self.url, "")
    self.assertEqual(self.indexer.index, {})

  def test_index_structure_correct(self):
    self.indexer.add_page(self.url, "hello")
    entry = self.indexer.index["hello"][self.url]
    self.assertIn("frequency", entry)
    self.assertIn("positions", entry)

# Test the build method to ensure it processes multiple pages and returns the index.
class TestBuild(unittest.TestCase):
  def setUp(self):
    self.indexer = Indexer()

  def test_builds_from_multiple_pages(self):
    pages = {
      "https://quotes.toscrape.com":         "life is good",
      "https://quotes.toscrape.com/page/2/": "life is short",
    }
    self.indexer.build(pages)
    self.assertIn("life", self.indexer.index)
    self.assertEqual(len(self.indexer.index["life"]), 2)

  def test_returns_index(self):
    pages = {"https://quotes.toscrape.com": "hello world"}
    result = self.indexer.build(pages)
    self.assertIsInstance(result, dict)

  def test_empty_pages_produces_empty_index(self):
    self.indexer.build({})
    self.assertEqual(self.indexer.index, {})

  def test_word_count_correct(self):
    pages = {"https://quotes.toscrape.com": "one two three"}
    self.indexer.build(pages)
    self.assertEqual(len(self.indexer.index), 3)

# Test the save and load methods to ensure the index can be saved to and loaded from disk correctly.
class TestSaveLoad(unittest.TestCase):
  def setUp(self):
    self.indexer = Indexer()
    self.indexer.add_page("https://quotes.toscrape.com", "hello world hello")

  def test_save_creates_file(self):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
      path = f.name
    try:
      self.indexer.save(path)
      self.assertTrue(os.path.exists(path))
    finally:
      os.remove(path)

  def test_save_and_load_roundtrip(self):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
      path = f.name
    try:
      self.indexer.save(path)
      new_indexer = Indexer()
      new_indexer.load(path)
      self.assertEqual(new_indexer.index, self.indexer.index)
    finally:
      os.remove(path)

  def test_saved_file_is_valid_json(self):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
      path = f.name
    try:
      self.indexer.save(path)
      with open(path) as f:
        data = json.load(f)
      self.assertIsInstance(data, dict)
    finally:
      os.remove(path)

  def test_load_nonexistent_file_returns_none(self):
    new_indexer = Indexer()
    result = new_indexer.load("/nonexistent/path/index.json")
    self.assertIsNone(result)

  def test_save_error_handled_gracefully(self):
    # Should not crash when given an invalid path
    self.indexer.save("/nonexistent/path/index.json")

  def test_load_returns_index(self):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
      path = f.name
    try:
      self.indexer.save(path)
      new_indexer = Indexer()
      result = new_indexer.load(path)
      self.assertIsInstance(result, dict)
    finally:
      os.remove(path)


if __name__ == "__main__":
  unittest.main()