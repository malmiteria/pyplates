from parser.code_block import CodeBlock, Statement
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
    for block, parsed in list(for_block.all_replacement(file_content)):
        file_content = file_content.replace(block, parsed)
    return file_content
