from parser.statements import Statement
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
    if_statement = Statement(
        "if",
        clauses=["elif", "else"],
        repeatable_clauses=["elif"],
        expressionless_clauses=["else"],
        optional_clauses=["elif", "else"],
    )

    if_block = if_statement.pattern()

    elif_pattern = if_statement.statement("elif")
    for block, parsed in list(elifs_replacments(elif_pattern, if_block, file_content)):
        file_content = file_content.replace(block, parsed)

    return file_content

def get_elifs_content(elif_pattern, elif_els):
    for res_elif in re.finditer(elif_pattern, elif_els):
        yield ELIF.format(
            elifexpression=res_elif.group("elifexpression"),
            elifblock=res_elif.group("elifblock"),
        )

def elifs_replacments(elif_pattern, if_block, file_content):
    for match in re.finditer(if_block, file_content):
        start, stop = match.span()
        substring = file_content[start:stop]
        python_str = IF.format(ifexpression=match.group("ifexpression"), ifblock=match.group("ifblock"))
        if match.group("elifs"):
            for elif_str in get_elifs_content(elif_pattern, match.group("elifs")):
                python_str += elif_str
        if match.group("else"):
            python_str += ELSE.format(
                elseblock=match.group("elseblock"),
            )
        exec(python_str, globals())
        if_parsed = res
        yield substring, if_parsed
