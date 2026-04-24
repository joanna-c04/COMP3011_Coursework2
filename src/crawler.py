import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Crawls a website and returns the text contents of each page.
class Crawler:
  def __init__(self, base_url: str, politeness_window: float = 6.0):
    self.base_url = base_url
    self.politeness_window = politeness_window
    self.visited: set[str] = set()
    self.pages: dict[str, str] = {}

  # Private helpers
  # Returns true if the URL belongs to the same domain as base url.
  def _is_valid_url(self, url: str) -> bool:
    parsed_base = urlparse(self.base_url)
    parsed_url = urlparse(url)
    return (
      parsed_url.scheme in ("http", "https") and
      parsed_url.netloc == parsed_base.netloc
    )
  
  # Return the text from a parsed page.
  def _extract_text(self, soup: BeautifulSoup) -> str:
    content = []
    for quote_div in soup.find_all("div", class_ = "quote"):
      text = quote_div.find("span", class_ = "text")
      author = quote_div.find("small", class_ = "author")

      if text and author:
        content.append(f"{text.get_text(strip = True)} by {author.get_text(strip = True)}")
    
    return "\n".join(content)
  
# Each page is expected to have a next button. Returns None if its the last page.
  def _extract_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
    next_link = soup.find("li", class_ = "next")
    if next_link:
      anchor = next_link.find("a", href = True)
      if anchor:
        next_url = urljoin(current_url, anchor["href"])
        if self._is_valid_url(next_url):
          return next_url
    
    return None
  
  # Perform crawl using linear pagination.
  def crawl(self, save_path: str | None = None) -> dict[str, str]:
    queue = [self.base_url]
    while queue:
      url = queue.pop(0)
      if url in self.visited:
        continue
      print(f"Crawling: {url}")
      try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
      except requests.RequestException as e:
        print(f"[Error] Could not fetch {url}: {e}")
        self.visited.add(url)
        continue

      self.visited.add(url)
      soup = BeautifulSoup(response.text, "html.parser")
      text = self._extract_text(soup)
      self.pages[url] = text

      # Save to json file after each page
      if save_path:
        with open(save_path, "w", encoding = "utf-8") as f:
          json.dump(self.pages, f, indent = 2)
        print(f"Saved {len(self.pages)} pages to {save_path}")

      # Get next links and add to queue
      next_url = self._extract_links(soup, url)
      if next_url and next_url not in self.visited:
        queue.append(next_url)
      # Pause before next request
      if queue:
        print(f"Waiting {self.politeness_window}s...")
        time.sleep(self.politeness_window)
    
    print(f"Crawl complete - {len(self.pages)} pages fetched.")
    return self.pages