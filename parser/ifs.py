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

def statement(statement, expressionless=False):
    if expressionless:
        expression = ""
    else:
        expression =  "(?P<" + statement + "expression>[^(\%\})]*)"
    return "\{\% " + statement + expression + " \%\}(?P<" + statement + "block>[^(\{\%)]*)"

def repeatable_clause(clause):
    clause_pattern = statement(clause)
    return f"(?P<{clause}s>({clause_pattern})*)"

def end_statement(statement):
    return "\{\% end" + statement + " \%\}"


def parse_ifs(file_content):
    if_pattern = statement("if")
    elifs_pattern = repeatable_clause("elif")
    else_pattern = statement("else", expressionless=True)
    else_opt_pattern = f"({else_pattern})?"
    endif_pattern = end_statement("if")
    if_block = if_pattern + elifs_pattern + else_opt_pattern + endif_pattern

    elif_pattern = statement("elif")
    for res in re.finditer(if_block, file_content):
        elif_els = res.group("elifs")
        elifs_expr, elifs_block = "", ""
        if elif_els:
            elifs_expr, elifs_block = zip(*get_elifs_content(elif_pattern, elif_els))

        if_parsed = make_python_if(
            res.group("ifexpression"),
            res.group("ifblock"),
            elifs_expr=elifs_expr,
            elifs_block=elifs_block,
            else_block=res.group("elseblock"),
        )
        file_content = re.sub(if_block, if_parsed, file_content)
    return file_content

def get_elifs_content(elif_pattern, elif_els):
    for res_elif in re.finditer(elif_pattern, elif_els):
        yield res_elif.group("elifexpression"), res_elif.group("elifblock")
