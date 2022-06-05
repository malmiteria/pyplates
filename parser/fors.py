from parser.statements import Statement
import re

FOR = """
res = "".join("{forblock}"for {forexpression})
"""

def make_python_for(expression, block):
    python_for = FOR.format(forexpression=expression, forblock=block)
    exec(python_for, globals())
    return res

def parse_fors(file_content):
    for_statement = Statement(
        "for",
    )
    for_block = for_statement.pattern()
    for res in re.finditer(for_block, file_content):
        for_parsed = make_python_for(
            res.group("forexpression"),
            res.group("forblock")
        )
        file_content = re.sub(for_block, for_parsed, file_content)
    return file_content
