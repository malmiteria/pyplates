from parser import render


def test_if():
    file_content = """{% if True %}WEEE{% endif %}"""

    assert render(file_content) == "WEEE"

def test_if_true_with_else():
    file_content = """{% if True %}WEEE{% else %}NOOOO{% endif %}"""

    assert render(file_content) == "WEEE"

def test_if_false_with_else():
    file_content = """{% if False %}WEEE{% else %}NOOOO{% endif %}"""

    assert render(file_content) == "NOOOO"

def test_if_2_elifs_else_FFF():
    file_content = """{% if False %}c1{% elif False %}c2{% elif False %}c3{% else %}else{% endif %}"""

    assert render(file_content) == "else"

def test_if_2_elifs_else_FFT():
    file_content = """{% if False %}c1{% elif False %}c2{% elif True %}c3{% else %}else{% endif %}"""

    assert render(file_content) == "c3"

def test_if_2_elifs_else_FTT():
    file_content = """{% if False %}c1{% elif True %}c2{% elif True %}c3{% else %}else{% endif %}"""

    assert render(file_content) == "c2"

def test_if_2_elifs_else_TTT():
    file_content = """{% if True %}c1{% elif True %}c2{% elif True %}c3{% else %}else{% endif %}"""

    assert render(file_content) == "c1"


def test_for():
    file_content = """{% for _ in range(5) %}O{% endfor %}"""

    assert render(file_content) == "OOOOO"


def test_for_in_if_true():
    file_content = """{% if True %}{% for _ in range(5) %}O{% endfor %}{% endif %}"""

    assert render(file_content) == "OOOOO"

def test_for_in_if_false():
    file_content = """{% if False %}{% for _ in range(5) %}O{% endfor %}{% endif %}"""

    assert render(file_content) == ""
