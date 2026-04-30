

# Web Page Text Analyzer

<img width="98" height="28" alt="image" src="https://github.com/user-attachments/assets/8ca95177-50e4-4296-86b7-64355da59a2f" />
Video Demo: https://youtu.be/FsWXTl3krjE



## What is this project?

Web Page Text Analyzer is a command-line Python tool that lets you scrape any public webpage and instantly analyze its text content. You paste in a URL, and the program fetches the page, strips out all the HTML noise, and gives you a breakdown of the text — how many words it has, how readable it is, which words appear most often, and more. At the end you can save the full report to a text file.

I built this because I wanted a project that touched two things at once: pulling real data from the internet and actually doing something useful with it. A lot of web scrapers just dump raw HTML or print a wall of text. This one processes what it finds and turns it into something readable and informative.

## Files in this project

**`project.py`** — This is the main file and contains everything: the four core functions and the `main()` entry point.

- `scrape\_text(url)` takes a URL string, validates it, makes an HTTP GET request using the `requests` library, and parses the response with BeautifulSoup. Before extracting the text it removes all `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, and `<aside>` tags because those tend to be full of JavaScript code, menu links, and other content that would completely skew the word counts and readability scores. It then pulls all remaining text, collapses extra whitespace, and returns a clean string.

- `get\_word\_frequency(text, top\_n=10)` takes the cleaned text and counts how often each word appears, returning the top N most frequent ones. It filters out short words (under 3 characters) and a hardcoded list of common English stop words like "the", "and", "is", etc. Without this filtering, every article's most common words would just be "the", "a", "and" — which tells you nothing interesting about the content.

- `compute\_text\_stats(text)` calculates six statistics about the text: total character count (excluding spaces), word count, sentence count, average word length, average sentence length, and a readability level. The readability level is based on average sentence length — short sentences score "Easy", very long ones score "Complex". It's a simplified version of readability metrics like Flesch-Kincaid, not a perfect science, but useful as a rough indicator.

- `save\_report(text, stats, freq, output\_path)` takes all the computed data and writes a neatly formatted plain-text report to a file. It includes the stats, the top keywords with their counts, and a 500-character preview of the scraped text.

- `main()` ties everything together as an interactive CLI. It asks for a URL, runs the scrape, prints the results to the terminal, and asks if you want to save a report.

**`test\_project.py`** — Contains 23 pytest tests covering all four functions. The scraper tests use `unittest.mock.patch` to mock out the actual HTTP requests so the tests run offline and don't depend on any live website being up. The other functions are tested with plain string inputs.

**`requirements.txt`** — Lists the three pip-installable dependencies: `requests` for HTTP, `beautifulsoup4` for HTML parsing, and `pytest` for running the tests.

## Design choices and tradeoffs

The biggest decision was how to handle the stop word list. I could have used a library like `nltk` which has a proper stop word corpus, but that felt like overkill for what this project needs and would add a heavy dependency. A hardcoded set of the most common English words works fine for the purpose of surfacing meaningful keywords from a webpage.

I also debated whether to support scraping multiple URLs in one run or let users input text from a local file instead of a URL. I kept it to a single URL per run to keep the interface simple and the code easy to follow. Adding multi-URL support would mostly just be a loop around what's already there, but it would complicate the output and the report format, so I left it out.

For the readability metric I chose average sentence length as the signal rather than syllable counting (which Flesch-Kincaid uses). Counting syllables accurately in Python without a dictionary library is surprisingly tricky and error-prone. Sentence length is a decent proxy and much simpler to compute reliably.

One thing I specifically wanted to avoid was having the program crash silently or give confusing errors when a URL is bad or a site is down. The `scrape\_text` function catches connection errors, timeouts, and HTTP errors separately and raises a `ValueError` with a helpful message in each case, so `main()` can just catch that one exception type and tell the user what went wrong.

## How to run it

```
pip install -r requirements.txt
python project.py
python -m pytest test_project.py -v
```
