import re
from parser.ifs import if_block
from parser.fors import for_block

code_blocks = {
    "if": ["elif", "else"],
    "for": ["else"],
    "try": ["except", "else", "finally"],
}

openners = "|".join(code_blocks.keys())
closers = "|".join(["end" + key for key in code_blocks.keys()])
clauses = "|".join(["|".join(value) for value in code_blocks.values()])
all_statement = "|".join([openners, clauses, closers])

def pattern(els):
    return "\{\% (" + els + ")[^\%\}]* \%\}"

def RUN(file_content):
    statement_by_start_index = []
    for occ in re.finditer(pattern(openners), file_content):
        statement_by_start_index.append(("OPEN", occ))
    for occ in re.finditer(pattern(clauses), file_content):
        statement_by_start_index.append(("CLAUSES", occ))
    for occ in re.finditer(pattern(closers), file_content):
        statement_by_start_index.append(("END", occ))
    statement_by_start_index = sorted(statement_by_start_index, key=lambda x: x[1].start())

    open_counter = None
    block = []
    for statement, match in statement_by_start_index:
        if open_counter is None: # outside any blocks
            if statement != "OPEN":
                continue # found a clause / end block, without corresponding start block
            block.append(match.span())
            open_counter = 0 # if facing open statement, we enter block
            continue
        if open_counter == 0: # inside open block, but not inside any nested block
            if statement == "END":
                block.append(match.span())
                yield block # sends out full block (with its clauses) and then resets block to prepare next yield
                open_counter = None
                block = []
                continue
            elif statement == "CLAUSES":
                block.append(match.span()) # not in nested block, so it is a clause of that block
                continue
        # no matter if nested or not, but we are in open block
        if statement == "OPEN":
            open_counter += 1
        if statement == "END":
            open_counter -= 1


# yield before any openners
# yield the openner
# yield from the openner block
##### repeat for all clauses
# yield the clause
# yield from the clause block
##### stop repeat for all clauses
# ignore end
# yield until next block

def indent(block):
    __, stop = next(block)
    for iter_start, iter_stop in block:
       yield stop, iter_start
       stop = iter_stop


def make_python_code(file_content, tab_level=0):
    start = 0
    for block in RUN(file_content):
        if file_content[start:block[0][0]]:
            yield "    " * tab_level + file_content[start:block[0][0]]
        for ((block_start, block_stop), (indent_start, indent_stop)) in zip(block, indent(iter(block))):
            yield "    " * tab_level + file_content[block_start + 3:block_stop - 3] + ":\n"
            yield from make_python_code(file_content[indent_start:indent_stop], tab_level=tab_level + 1)
        start = block[-1][-1]
    if file_content[start:]:
        yield "    " * tab_level + file_content[start:]

def render(file_content, *args, **kwargs):
    print("".join(make_python_code(file_content)))
                
    for block, parsed in list(for_block.all_replacement(file_content)):
        file_content = file_content.replace(block, parsed)
    for block, parsed in list(if_block.all_replacement(file_content)):
        file_content = file_content.replace(block, parsed)
    return file_content
