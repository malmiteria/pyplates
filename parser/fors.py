from parser.code_block import CodeBlock, Statement
import re

FOR = """
res = "".join("{forblock}"for {forexpression})
"""
for_block = CodeBlock(
    Statement(
        FOR, "for",
    )
)
