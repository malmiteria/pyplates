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

def make_python_if(if_expr, if_block, elifs_expr="", elifs_blocks="", else_block=""):
    if elifs_expr:
        elifs = "".join(ELIF.format(elifexpression=elif_expr, elifblock=elif_block) for elif_expr, elif_block in zip(elifs_expr, elifs_blocks))
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

    if_block = "\{\% if (?P<ifexpression>[^(\%\})]*) \%\}(?P<ifblock>[^(\{\%)]*)(\{\% elif (?P<elifexpression>[^(\%\})]*) \%\}(?P<elifblock>[^(\%\})]*))*(\{\% else \%\}(?P<elseblock>[^(\%\})]*))?\{\% endif \%\}"
    for res in re.finditer(if_block, file_content):
        if_parsed = make_python_if(
            res.group("ifexpression"),
            res.group("ifblock"),
            [res.group("elifexpression")],
            [res.group("elifblock")],
            else_block=res.group("elseblock"),
        )
        file_content = re.sub(if_block, if_parsed, file_content)
    return file_content
