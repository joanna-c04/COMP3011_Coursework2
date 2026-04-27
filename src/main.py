import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from crawler import Crawler
from indexer import Indexer

TARGET_URL = "https://quotes.toscrape.com"
POLITENESS_WINDOW = 6.0
PAGES_PATH = "/Users/joanna/Library/CloudStorage/OneDrive-UniversityofLeeds/One Drive - CompSci/Year 3/Semester 2/COMP3011 - Web Services and Web Sata/Assessment/Coursework 2/code/data/pages.json"
INDEX_PATH = "/Users/joanna/Library/CloudStorage/OneDrive-UniversityofLeeds/One Drive - CompSci/Year 3/Semester 2/COMP3011 - Web Services and Web Sata/Assessment/Coursework 2/code/data/index.json"

def print_help() -> None:
  print("\nAvailable commands:")
  print("build - Crawl the website and display fetched pages")
  print("index - Build the inverted index from saved pages")
  print("help - Show this message")
  print("quit - Exit\n")

def main() -> None:
  print("Search Engline")
  print_help()

  while True:
    try:
      raw = input(">").strip()
    except(EOFError, KeyboardInterrupt):
      print("\nExiting...")
      break

    if not raw:
      continue

    command = raw.split()[0].lower()
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