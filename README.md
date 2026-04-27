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

## How to run the tests:
1. In the code directory, change directory to tests using: <i>cd tests/</i>
2. To run the crawler test use: <i>python -m pytest test_crawler.py -v</i>
3. To run the indexer test use: <i>python -m pytest test_indexer.py -v</i>