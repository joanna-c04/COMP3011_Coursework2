class Searcher:
  def __init__(self, index):
    self.index = index

  def print_word(self, word):
    """
    Print the full index entry for a word. Shows every page it appears on with frequency and position.
    """
    word = word.lower().strip()
    if not word:
      print("[Error] No word provided.")
      return
    if word not in self.index:
      print(f"'{word}' not found in index.")
      return
    
    entries = self.index[word]
    print(f"Inverted index for '{word}' ({len(entries)} page(s)):")
    for url, stats in entries.items():
      print(f"URL: {url}")
      print(f"Frequency: {stats['frequency']}")
      print(f"Positions: {stats['positions']}")

  def find(self, query):
    """
    Find all pages containing every word in the query.
    Results are ranked by combined word frequency.
    """
    query = query.lower().strip()
    if not query:
      print("[Error] No query provided.")
      return []
    words = query.split()
    # Checks all words are in the query
    missing = [w for w in words if w not in self.index]
    if missing:
      print(f"Words not found in index: {', '.join(missing)}")
      return []
  
    page_sets = [set(self.index[w].keys()) for w in words]
    common_pages = page_sets[0].intersection(*page_sets[1:])

    if not common_pages:
      print("No pages contain all query words.")
      return []
    
    def combined_frequency(url):
      """
      Rank by combined frequency across all query words.
      """
      return sum(self.index[word][url]["frequency"] for word in words)
    ranked = sorted(common_pages, key=combined_frequency, reverse=True)
    print(f"Found {len(ranked)} page(s) containing all query words:")
    for i, url in enumerate(ranked, start = 1):
      frequency = {word: self.index[word][url]["frequency"] for word in words}
      print(f"{i}. {url} (frequencies: {frequency})")
    
    return ranked