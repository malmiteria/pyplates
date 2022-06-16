import unittest

from parser import render



#### Test simple
class TestCaseIf(unittest.TestCase):
    def test_if(self):
        file_content = """{% if True %}WEEE{% endif %}"""

        assert render(file_content) == "WEEE"

    def test_empty_if(self):
        file_content = """{% if True %}{% endif %}"""

        assert render(file_content) == ""

    def test_if_true_with_else(self):
        file_content = """{% if True %}WEEE{% else %}NOOOO{% endif %}"""

        assert render(file_content) == "WEEE"

    def test_if_false_with_else(self):
        file_content = """{% if False %}WEEE{% else %}NOOOO{% endif %}"""

        assert render(file_content) == "NOOOO"

    def test_if_2_elifs_else_FFF(self):
        file_content = """{% if False %}c1{% elif False %}c2{% elif False %}c3{% else %}else{% endif %}"""

        assert render(file_content) == "else"

    def test_if_2_elifs_else_FFT(self):
        file_content = """{% if False %}c1{% elif False %}c2{% elif True %}c3{% else %}else{% endif %}"""

        assert render(file_content) == "c3"

    def test_if_2_elifs_else_FTT(self):
        file_content = """{% if False %}c1{% elif True %}c2{% elif True %}c3{% else %}else{% endif %}"""

        assert render(file_content) == "c2"

    def test_if_2_elifs_else_TTT(self):
        file_content = """{% if True %}c1{% elif True %}c2{% elif True %}c3{% else %}else{% endif %}"""

        assert render(file_content) == "c1"


class TestCaseConsecutiveIf(unittest.TestCase):
    def test_two_ifs_TT(self):
        file_content = """{% if True %}c1{% endif %}{% if True %}c2{% endif %}"""

        assert render(file_content) == "c1c2"

    def test_two_ifs_TF(self):
        file_content = """{% if True %}c1{% endif %}{% if False %}c2{% endif %}"""

        assert render(file_content) == "c1"

    def test_two_ifs_FT(self):
        file_content = """{% if False %}c1{% endif %}{% if True %}c2{% endif %}"""

        assert render(file_content) == "c2"

    def test_two_ifs_FF(self):
        file_content = """{% if False %}c1{% endif %}{% if False %}c2{% endif %}"""

        assert render(file_content) == ""


class TestCaseNestedIf(unittest.TestCase):
    def test_nested_ifs_TT(self):
        file_content = """{% if True %}{% if True %}TT{% endif %}{% endif %}"""

        assert render(file_content) == "TT"

    def test_nested_ifs_FT(self):
        file_content = """{% if False %}{% if True %}TT{% endif %}{% endif %}"""

        assert render(file_content) == ""

    def test_nested_ifs_TF(self):
        file_content = """{% if True %}{% if False %}TT{% endif %}{% endif %}"""

        assert render(file_content) == ""

    def test_nested_complex_ifs(self):
        file_content = """{% if False %}{% if True %}TT{% elif True %}FTelif{% else %}Felse{% endif %}{% elif True %}elif{% else %}else{% endif %}"""

        assert render(file_content) == "elif"
