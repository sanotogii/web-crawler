import sys
import asyncio
from crawl import *
from json_report import write_json_report

def main():
    if len(sys.argv) != 4:
        print("usage: uv run main.py URL max_concurrency max_pages")
        sys.exit(1)

    url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])
    pages = asyncio.run(crawl_page(url, max_concurrency, max_pages))
    write_json_report(pages)


if __name__ == "__main__":
    main()
