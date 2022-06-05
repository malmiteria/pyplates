from parser.statements import CodeBlock, Statement, Clause
import re

ELIF = """elif {elifexpression}:
    res = "{elifblock}"
"""
ELSE = """else:
    res = "{elseblock}"
"""
IF = """
res = ""
if {ifexpression}:
    res = "{ifblock}"
"""

def parse_ifs(file_content):
    if_block = CodeBlock(
        Statement(IF, "if"),
        clause_list=[
            Clause(ELIF, "elif", repeatable=True, optional=True),
            Clause(ELSE, "else", expressionless=True, optional=True),
        ]
    )
    for block, parsed in list(elifs_replacments(if_block, file_content)):
        file_content = file_content.replace(block, parsed)

    return file_content

def elifs_replacments(if_block, file_content):
    for match in re.finditer(if_block.pattern(), file_content):
        start, stop = match.span()
        substring = file_content[start:stop]
        python_str = if_block.python_str(match)
        exec(python_str, globals())
        if_parsed = res
        yield substring, if_parsed
