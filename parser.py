import re

FOR = """
res = "".join("{forblock}"for {forexpression})
"""

def make_python_for(expression, block):
    python_for = FOR.format(forexpression=expression, forblock=block)
    exec(python_for, globals())
    return res

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


def render(file_content, *args, **kwargs):
    for_block = "\{\% for (?P<forexpression>.*) \%\}(?P<forblock>.*)\{\% endfor \%\}"
    for res in re.finditer(for_block, file_content):
        for_parsed = make_python_for(
            res.group("forexpression"),
            res.group("forblock")
        )
        file_content = re.sub(for_block, for_parsed, file_content)

    elif_pattern = "\{\% elif (?P<elifexpression>[^(\%\})]*) \%\}(?P<elifblock>[^(\{\%)]*)"
    elifs_pattern = f"(?P<elifs>({elif_pattern})*)"
    if_block = "\{\% if (?P<ifexpression>[^(\%\})]*) \%\}(?P<ifblock>[^(\{\%)]*)" + elifs_pattern + "(\{\% else \%\}(?P<elseblock>[^(\%\})]*))?\{\% endif \%\}"
    for res in re.finditer(if_block, file_content):
        elif_els = res.group("elifs")
        elifs_expr, elifs_block = "", ""
        if elif_els:
            elifs_expr, elifs_block = zip(*get_elifs_content(elif_pattern, elif_els))

        if_parsed = make_python_if(
            res.group("ifexpression"),
            res.group("ifblock"),
            elifs_expr = elifs_expr,
            elifs_block = elifs_block,
            else_block=res.group("elseblock"),
        )
        file_content = re.sub(if_block, if_parsed, file_content)
    return file_content

def get_elifs_content(elif_pattern, elif_els):
    for res_elif in re.finditer(elif_pattern, elif_els):
        yield res_elif.group("elifexpression"), res_elif.group("elifblock")
