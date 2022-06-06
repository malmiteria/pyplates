from parser import render


#### Test simple
def test_if():
    file_content = """{% if True %}WEEE{% endif %}"""

    assert render(file_content) == "WEEE"

def test_empty_if():
    file_content = """{% if True %}{% endif %}"""

    assert render(file_content) == ""

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

def test_empty_for():
    file_content = """{% for _ in range(5) %}{% endfor %}"""

    assert render(file_content) == ""

### test two patterns
def test_two_ifs_TT():
    file_content = """{% if True %}c1{% endif %}{% if True %}c2{% endif %}"""

    assert render(file_content) == "c1c2"

def test_two_ifs_TF():
    file_content = """{% if True %}c1{% endif %}{% if False %}c2{% endif %}"""

    assert render(file_content) == "c1"

def test_two_ifs_FT():
    file_content = """{% if False %}c1{% endif %}{% if True %}c2{% endif %}"""

    assert render(file_content) == "c2"

def test_two_ifs_FF():
    file_content = """{% if False %}c1{% endif %}{% if False %}c2{% endif %}"""

    assert render(file_content) == ""

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
    file_content = """{% for _ in range(3) %}{% for _ in range(5) %}O{% endfor %}{% endif %}"""

    assert render(file_content) == "OOOOOOOOOOOOOOO"

def test_nested_complex_ifs():
    file_content = """{% if False %}{% if True %}TT{% elif True %}FTelif{% else %}Felse{% endif %}{% elif True %}elif{% else %}else{% endif %}"""

    assert render(file_content) == "elif"

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
