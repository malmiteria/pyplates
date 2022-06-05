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
    for block, parsed in list(for_replacments(for_block, file_content)):
        file_content = file_content.replace(block, parsed)
    return file_content

def for_replacments(for_block, file_content):
    for res in re.finditer(for_block, file_content):
        start, stop = res.span()
        substring = file_content[start:stop]
        for_parsed = make_python_for(
            res.group("forexpression"),
            res.group("forblock")
        )
        yield substring, for_parsed

