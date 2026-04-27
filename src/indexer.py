import json
import re

class Indexer:
  def __init__(self):
    self.index = {}

  def _tokenise(self, text):
    """
    Split text into lowercase word tokens, stripping punctuation.
    """
    tokens = re.findall(r"[a-zA-Z]+", text)
    
    return [token.lower() for token in tokens]
  
  def add_page(self, url, text):
    """
    Tokenise the text and add each word to the inverted index.
    """
    tokens = self._tokenise(text)
    for position, word in enumerate(tokens):
      if word not in self.index:
        self.index[word] = {}
      if url not in self.index[word]:
        self.index[word][url] = {"frequency": 0, "positions": []}
      self.index[word][url]["frequency"] += 1
      self.index[word][url]["positions"].append(position)

  def build(self, pages):
    """
    Build the inverted index produced by the crawler.
    """
    print(f"Building index from {len(pages)} pages...")
    for url, text in pages.items():
      self.add_page(url, text)
    print(f"Index built with {len(self.index)} unique words.")

    return self.index
  
  def save(self, filepath):
    try:
      with open(filepath, "w", encoding="utf-8") as f:
        json.dump(self.index, f, indent=2, ensure_ascii=False)
      print(f"Index saved to {filepath}")
    except OSError as e:
      print(f"Error saving index to {filepath}: {e}")
  
  def load(self, filepath):
    try:
      with open(filepath, "r", encoding="utf-8") as f:
        self.index = json.load(f)
      print(f"Index loaded from {filepath}")
      return self.index
    except FileNotFoundError:
      print(f"[Error] No index file found at {filepath}. Run 'build' first.")
      return None
    except OSError as e:
      print(f"[Error] Could not load index: {e}")
      return None