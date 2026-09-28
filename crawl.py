from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
import asyncio
import aiohttp
import requests
from typing import TypedDict
from urllib.parse import urlsplit


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    normalized_url = url

    for word in ["http://", "https://"]:
        normalized_url = normalized_url.replace(word, "")

    if normalized_url.endswith("/"):
        normalized_url = normalized_url[:-1]

    return normalized_url

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("h1")

    return title.text if title is not None else ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    urls = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href is not None:
            urls.append(urljoin(base_url, href))

    return urls

  

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    first_p = main.find("p") if main is not None else soup.find("p")

    return first_p.text if first_p is not None else ""

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for image in soup.find_all("img"):
        src = image.get("src")

        if src is not None:
            urls.append(urljoin(base_url, src))

    return urls

def extract_page_data(html: str, page_url: str):
    data = dict()
    data["url"] = page_url
    data["heading"] = get_heading_from_html(html)
    data["first_paragraph"] = get_first_paragraph_from_html(html)
    data["outgoing_links"] = get_urls_from_html(html, page_url)
    data["image_urls"] = get_images_from_html(html, page_url)

    return data

def get_html(url):
    response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "text/html" not in content_type:
        raise Exception("Response is not HTML")

    return response.text

class AsyncCrawler:
    def __init__(self, max_concurrency: int, max_pages: int):
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.visited: set[str] = set()
        self.pages: dict[str, PageData] = {}
        self.should_stop = False
        self.all_tasks: set[asyncio.Task[None]] = set()
        self.base_url = ""

    def add_page_visit(self, url: str) -> bool:
        if self.should_stop:
            return False

        normalized_url = normalize_url(url)
        if normalized_url in self.visited:
            return False

        if len(self.visited) >= self.max_pages:
            self.should_stop = True
            print("Reached maximum number of pages to crawl.")
            return False

        self.visited.add(normalized_url)
        return True

    async def get_html(self, url: str) -> str | None:
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, headers={"User-Agent": "BootCrawler/1.0"}
                    ) as response:
                        response.raise_for_status()
                        if "text/html" not in response.headers.get("Content-Type", ""):
                            return None
                        return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return

        base_url_obj = urlsplit(self.base_url)
        current_url_obj = urlsplit(current_url)
        if current_url_obj.netloc != base_url_obj.netloc:
            return

        if not self.add_page_visit(current_url):
            return

        print(f"crawling {current_url}")
        html = await self.get_html(current_url)
        if html is None:
            return

        page_info = extract_page_data(html, current_url)
        self.pages[normalize_url(current_url)] = page_info

        tasks = []
        for next_url in page_info["outgoing_links"]:
            if self.should_stop:
                break
            task = asyncio.create_task(self.crawl_page(next_url))
            self.all_tasks.add(task)
            tasks.append(task)

        for task in tasks:
            try:
                await task
            finally:
                self.all_tasks.discard(task)

    async def crawl(self, base_url: str) -> dict[str, PageData]:
        self.base_url = base_url
        await self.crawl_page(base_url)
        return self.pages


async def crawl_page(
    base_url: str, max_concurrency: int, max_pages: int
) -> dict[str, PageData]:
    crawler = AsyncCrawler(max_concurrency, max_pages)
    return await crawler.crawl(base_url)
