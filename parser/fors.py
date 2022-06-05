from parser.statements import CodeBlock, Statement
import re

FOR = """
res = "".join("{forblock}"for {forexpression})
"""

def parse_fors(file_content):
    for_block = CodeBlock(
        Statement(
            FOR, "for",
        )
    )
    for block, parsed in list(for_replacments(for_block, file_content)):
        file_content = file_content.replace(block, parsed)
    return file_content

def for_replacments(for_block, file_content):
    for match in re.finditer(for_block.pattern(), file_content):
        start, stop = match.span()
        substring = file_content[start:stop]
        python_str = for_block.python_str(match)
        exec(python_str, globals())
        for_parsed = res
        yield substring, for_parsed

