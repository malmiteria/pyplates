import unittest

from parser import render



def test_no_blocks():
    file_content = """why would you use this module on this file?"""

    assert render(file_content) == "why would you use this module on this file?"


def test_special_characters():
    # this file contains special characters for python (including newline, which apparently happens at the end of the last line)
    with open("tests/files/special_characters.txt") as f:
        file_content = f.read()

    assert render(file_content) == "\"\'\\\n"


class TestCaseFor(unittest.TestCase):
    def test_for(self):
        file_content = """{% for _ in range(5) %}O{% endfor %}"""

        assert render(file_content) == "OOOOO"

    def test_empty_for(self):
        file_content = """{% for _ in range(5) %}{% endfor %}"""

        assert render(file_content) == ""

    # TODO: test_for_else (requires break)

    def test_for_else_no_break(self):
        file_content = """{% for _ in range(5) %}O{% else %}ELSE{% endfor %}"""

        assert render(file_content) == "OOOOOELSE"

### test two patterns

def test_two_for():
    file_content = """{% for _ in range(5) %}O{% endfor %}{% for _ in range(5) %}A{% endfor %}"""

    assert render(file_content) == "OOOOOAAAAA"

def test_if_for():
    file_content = """{% if True %}O{% endif %}{% for _ in range(5) %}A{% endfor %}"""

    assert render(file_content) == "OAAAAA"

def test_for_if():
    file_content = """{% for _ in range(5) %}A{% endfor %}{% if True %}O{% endif %}"""

    assert render(file_content) == "AAAAAO"

##### test nested
def test_nested_for():
    file_content = """{% for _ in range(3) %}{% for _ in range(5) %}O{% endfor %}{% endfor %}"""

    assert render(file_content) == "OOOOOOOOOOOOOOO"

def test_for_in_if_true():
    file_content = """{% if True %}{% for _ in range(5) %}O{% endfor %}{% endif %}"""

    assert render(file_content) == "OOOOO"

def test_for_in_if_false():
    file_content = """{% if False %}{% for _ in range(5) %}O{% endfor %}{% endif %}"""

    assert render(file_content) == ""

def test_if_true_in_for():
    file_content = """{% for _ in range(5) %}{% if True %}O{% endif %}{% endfor %}"""

    assert render(file_content) == "OOOOO"

def test_if_false_in_for():
    file_content = """{% for _ in range(5) %}{% if False %}O{% endif %}{% endfor %}"""

    assert render(file_content) == ""





###### TEST ERRORS
class TestCaseErrors(unittest.TestCase):
    def test_unmatched_open(self):
        file_content = """{% if False %}"""

        with self.assertRaises(ValueError, expected_regex="^statement if opened but never closed.$") as e:
            render(file_content)

    def test_unmatched_closer(self):
        file_content = """{% endif %}"""

        with self.assertRaises(ValueError, expected_regex="^statement if closed but never opened.$") as e:
            render(file_content)

    def test_closers_in_mixed_order_should_raise_error(self):
        file_content = """{% for _ in range(5) %}{% if False %}O{% endfor %}{% endif %}"""

        with self.assertRaisesRegex(ValueError, expected_regex="^statement for closed by if closer.$"):
            render(file_content)
