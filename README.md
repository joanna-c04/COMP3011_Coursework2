# COMP3011_Coursework2
## Project overview:
This project crawls the website: "https://quotes.toscrape.com/", and creates an inverted index of all word occurences in the pages of the website. Additionally, it allows the user to find pages conaining certain search terms.

## How to run this project:
1. Download the project .zip file and unzip.
2. Install the dependencies using: <i>pip install -r requirements.txt</i>
3. Run the main script: <i> cd src <i>
  </br><i> python main.py </i>
4. Type <i>build</i> to build the pages.json.
 - This crawls the webpage and compiles all text into pages.json.
5. Type <i>index</i> to index pages.json.
- This counts and tracks the position of every work in pages.json and returns it to index.json.
6. Type <i>load</i> to load index.json into memory without re-crawling or re-indexing.
7. Type <i>print word</i> to look up a single word.
- It displays every page it appears on, the frequency on each page, and its position(s). eg. <i>print love</i>.
8. Type <i>find query</i> to search the index for one or more words.
- It uses AND search to find and return all pages containing every word in the query. The results are ranked by combined word frequency, so the most relevant page appears first. eg. <i>find love life</i>.
9. Type <i>help</i> to display the list of available commands.
10. Type <i>quit</i> to exit the program. 

## How to run the tests:
1. In the code directory, change directory to tests using: <i>cd tests/</i>
2. To run the crawler test use: <i>python -m pytest test_crawler.py -v</i>
3. To run the indexer test use: <i>python -m pytest test_indexer.py -v</i>
4. To run the search test use: <i>python -m pytest test_search.py -v</i>