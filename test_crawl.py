import unittest
from crawl import *



class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_removes_trailing_slash(self):
        actual = normalize_url("https://www.boot.dev/")
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_normalize_url_handles_http(self):
        actual = normalize_url("http://www.boot.dev/blog")
        expected = "www.boot.dev/blog"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_nested_text(self):
        input_body = "<html><body><h1><span>Test</span> Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_without_main(self):
        input_body = "<html><body><p>First paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/about">About</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/about"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_finds_all_links(self):
        input_url = "https://crawler-test.com"
        input_body = """
            <html><body>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
            </body></html>
        """
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/about",
            "https://crawler-test.com/contact",
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_skips_missing_href(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a>Missing href</a><a href="/about">About</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/about"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_finds_all_images(self):
        input_url = "https://crawler-test.com"
        input_body = """
            <html><body>
                <img src="/logo.png" alt="Logo">
                <img src="images/banner.png" alt="Banner">
            </body></html>
        """
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/logo.png",
            "https://crawler-test.com/images/banner.png",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_skips_missing_src(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="Missing source"><img src="/logo.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_empty(self):
        actual = get_images_from_html("<html><body></body></html>", "https://crawler-test.com")
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_without_links_or_images(self):
        input_url = "https://crawler-test.com/about"
        input_body = "<html><body><h1>About</h1><p>About us.</p></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": input_url,
            "heading": "About",
            "first_paragraph": "About us.",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
