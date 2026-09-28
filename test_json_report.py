import json
import os
import tempfile
import unittest

from json_report import write_json_report


class TestJsonReport(unittest.TestCase):
    def test_write_json_report_sorts_pages_by_url(self):
        page_data = {
            "b": {"url": "https://example.com/b"},
            "a": {"url": "https://example.com/a"},
        }

        with tempfile.NamedTemporaryFile(delete=False) as report_file:
            filename = report_file.name

        try:
            write_json_report(page_data, filename)
            with open(filename, encoding="utf-8") as report_file:
                report = json.load(report_file)
        finally:
            os.unlink(filename)

        self.assertEqual(report, [page_data["a"], page_data["b"]])


if __name__ == "__main__":
    unittest.main()
