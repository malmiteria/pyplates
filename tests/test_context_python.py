import unittest

from parser import render


class TestCaseContext(unittest.TestCase):
    def test_simple(self):
        file_content = """{{ value }}"""

        assert render(file_content, value="something") == "something"

    def test_double(self):
        file_content = """{{ value }}{{ value }}"""

        assert render(file_content, value="something") == "somethingsomething"

    def test_with_surroudings(self):
        file_content = """before {{ value }} middle {{ value }} after"""

        assert render(file_content, value="something") == "before something middle something after"

    def test_in_for(self):
        file_content = """{% for value in range(5) %}{{ value }}{% endfor %}"""

        assert render(file_content) == "01234"


class TestCaseRawPython(unittest.TestCase):

    def test_break_in_for(self):
        file_content = """{% for number in range(5) %}{% if number == 3 %}{{{ break }}}{% endif %}{{ number }}{% endfor %}"""

        assert render(file_content) == "012"

    def test_raw_python_yields(self):
        file_content = """{{{ yield str("a") }}}{{{ yield str("b") }}}"""

        assert render(file_content) == "ab"

    def test_set_and_use_value(self):
        file_content = """{{{ number = 10 }}}{{ number }}"""

        assert render(file_content) == "10"

    def test_set_triple_dict(self):
        file_content = """{{{ TD = {"k1": {"k2": {"k3": "A"}}} }}}{{ TD["k1"]["k2"]["k3"] }}"""

        assert render(file_content) == "A"
