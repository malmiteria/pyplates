from parser.code_block import CodeBlock, Statement, Clause
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
if_block = CodeBlock(
    Statement(IF, "if"),
    clause_list=[
        Clause(ELIF, "elif", repeatable=True, optional=True),
        Clause(ELSE, "else", expressionless=True, optional=True),
    ]
)
