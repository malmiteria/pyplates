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
    for block, parsed in list(if_block.all_replacement(file_content)):
        file_content = file_content.replace(block, parsed)

    return file_content
