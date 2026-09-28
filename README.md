# Scraper Job

An asynchronous web crawler that extracts page metadata, links, and image URLs
from a website and writes the results to a JSON report.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

Install the project dependencies with:

```bash
uv sync
```

## Usage

Run the crawler from the project root:

```bash
uv run main.py URL max_concurrency max_pages
```

Example:

```bash
uv run main.py https://learnwebscraping.dev/practice/ecommerce/ 3 10
```

Arguments:

- `URL`: The starting page for the crawl.
- `max_concurrency`: The maximum number of page requests running at once.
- `max_pages`: The maximum number of pages to crawl.

The crawler prints each page as it is visited and creates `report.json` in the
project root. The report is a JSON array sorted by page URL. Each page record
contains its URL, heading, first paragraph, outgoing links, and image URLs.

## Tests

Run the test suite with:

```bash
uv run -m unittest -v
```
