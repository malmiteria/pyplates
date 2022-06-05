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
{elifs}{else_block}
"""

def make_python_if(if_expr, if_block, elifs_expr="", elifs_block="", else_block=""):
    if elifs_expr:
        elifs = "".join(ELIF.format(elifexpression=elif_expr, elifblock=elif_block) for elif_expr, elif_block in zip(elifs_expr, elifs_block))
    else:
        elifs = ""
    else_block = ELSE.format(elseblock=else_block)
    python_if = IF.format(ifexpression=if_expr, ifblock=if_block, elifs=elifs, else_block=else_block)

    exec(python_if, globals())
    return res


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
        yield res_elif.group("elifexpression"), res_elif.group("elifblock")

def elifs_replacments(elif_pattern, if_block, file_content):
    for res in re.finditer(if_block, file_content):
        start, stop = res.span()
        substring = file_content[start:stop]
        elif_els = res.group("elifs")
        elifs_expr, elifs_block = "", ""
        if elif_els:
            elifs_expr, elifs_block = zip(*get_elifs_content(elif_pattern, elif_els))

        if_parsed = make_python_if(
            res.group("ifexpression"),
            res.group("ifblock"),
            elifs_expr=elifs_expr,
            elifs_block=elifs_block,
            else_block=res.group("elseblock") or "",
        )
        yield substring, if_parsed
