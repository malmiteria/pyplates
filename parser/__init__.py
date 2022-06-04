import re
from parser.ifs import parse_ifs

FOR = """
res = "".join("{forblock}"for {forexpression})
"""

def make_python_for(expression, block):
    python_for = FOR.format(forexpression=expression, forblock=block)
    exec(python_for, globals())
    return res

def render(file_content, *args, **kwargs):
    for_block = "\{\% for (?P<forexpression>.*) \%\}(?P<forblock>.*)\{\% endfor \%\}"
    for res in re.finditer(for_block, file_content):
        for_parsed = make_python_for(
            res.group("forexpression"),
            res.group("forblock")
        )
        file_content = re.sub(for_block, for_parsed, file_content)


    file_content = parse_ifs(file_content)
    return file_content
