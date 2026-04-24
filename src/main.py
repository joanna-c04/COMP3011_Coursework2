import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from crawler import Crawler

TARGET_URL = "https://quotes.toscrape.com"
POLITENESS_WINDOW = 6.0

def print_help() -> None:
  print("\nAvailable commands:")
  print("build - Crawl the website and display fetched pages")
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
    if command == "build":
      print(f"Crawling {TARGET_URL} with politeness window {POLITENESS_WINDOW} seconds...")
      crawler = Crawler(TARGET_URL, politeness_window = POLITENESS_WINDOW)
      pages = crawler.crawl(save_path = "/Users/joanna/Library/CloudStorage/OneDrive-UniversityofLeeds/One Drive - CompSci/Year 3/Semester 2/COMP3011 - Web Services and Web Sata/Assessment/Coursework 2/code/data/pages.json")

      if not pages:
        print("No pages were fetched.")
      else:
        print(f"Fetched {len(pages)} pages:")
        for url in pages:
          preview = pages[url][:80].replace("\n", " ")
          print(f"- {url}: {preview}...")
          
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