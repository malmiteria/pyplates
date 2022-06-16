import unittest

from parser import render


class TestCaseContext(unittest.TestCase):
    def test_simple(self):
        file_content = """{{ value }}"""

        assert render(file_content, value="something") == "something"

    def test_in_for(self):
        file_content = """{% for value in range(5) %}{{ value }}{% endfor %}"""

        assert render(file_content) == "01234"
