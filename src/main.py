import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from crawler import Crawler
from indexer import Indexer
from search import Searcher

TARGET_URL = "https://quotes.toscrape.com"
POLITENESS_WINDOW = 6.0
PAGES_PATH = "/Users/joanna/Library/CloudStorage/OneDrive-UniversityofLeeds/One Drive - CompSci/Year 3/Semester 2/COMP3011 - Web Services and Web Sata/Assessment/Coursework 2/code/data/pages.json"
INDEX_PATH = "/Users/joanna/Library/CloudStorage/OneDrive-UniversityofLeeds/One Drive - CompSci/Year 3/Semester 2/COMP3011 - Web Services and Web Sata/Assessment/Coursework 2/code/data/index.json"

def print_help() -> None:
  print("\nAvailable commands:")
  print("build - Crawl the website and display fetched pages")
  print("index - Build the inverted index from saved pages")
  print("load - Load the index from disk")
  print("print <word> - Print the index entry for a word")
  print("find <query> - Find pages containing all words in the query")
  print("help - Show this message")
  print("quit - Exit\n")

def main() -> None:
  print("Search Engline")
  print_help()

  searcher = None

  while True:
    try:
      raw = input(">").strip()
    except(EOFError, KeyboardInterrupt):
      print("\nExiting...")
      break

    if not raw:
      continue

    parts = raw.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Crawl the website from the fetched pages. Save to disk.
    if command == "build":
      print(f"Crawling {TARGET_URL} with politeness window {POLITENESS_WINDOW} seconds...")
      crawler = Crawler(TARGET_URL, politeness_window = POLITENESS_WINDOW)
      pages = crawler.crawl(save_path = PAGES_PATH)
      if not pages:
        print("No pages were fetched.")

    # If crawl has already been run and pages are saved.      
    elif command == "index":
      if not os.path.exists(PAGES_PATH):
        print("No pages.json found. Run 'build' first.")
        continue
      print(f"Loading pages from {PAGES_PATH}...")
      with open(PAGES_PATH, "r", encoding="utf-8") as f:
        pages = json.load(f)
      indexer = Indexer()
      indexer.build(pages)
      indexer.save(INDEX_PATH)
      print("Indexing complete.")

    # Load the index from disk.
    elif command == "load":
      if not os.path.exists(INDEX_PATH):
        print("No index.json found. Run 'index' first.")
        continue
      print(f"Loading index from {INDEX_PATH}...")
      indexer = Indexer()
      indexer.load(INDEX_PATH)
      searcher = Searcher(indexer.index)
      print("Index loaded. You can now use 'print <word>' and 'find <query>' commands.")

    elif command == "print":
      if searcher is None:
        print("No index loaded. Run 'load' first.")
        continue
      if not args:
        print("Usage: print <word>. eg. 'print life'")
        continue
      searcher.print_word(args)
      
    elif command == "find":
      if searcher is None:
        print("No index loaded. Run 'load' first.")
        continue
      if not args:
        print("Usage: find <query>. eg. 'find life good'")
        continue
      searcher.find(args)

    elif command in ("help", "?"):
      print_help()

    elif command in ("quit", "exit", "q"):
      print("Exiting...")
      break

    else:
      print(f"Unknown command: {command}. Type 'help' for options")
      print_help()

if __name__ == "__main__":
  main()