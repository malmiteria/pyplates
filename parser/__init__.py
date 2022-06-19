import re


class Parser:
    def __init__(self):
        self.code_blocks = {
            "if": ["elif", "else"],
            "for": ["else"],
            "try": ["except", "else", "finally"],
        }
        self.openners = "|".join(self.code_blocks.keys())
        self.closers = "|".join(["end" + key for key in self.code_blocks.keys()])
        self.clauses = "|".join(["|".join(value) for value in self.code_blocks.values()])

    def openners_matches(self, file_content):
        return re.finditer(self.pattern(self.openners), file_content)

    def closers_matches(self, file_content):
        return re.finditer(self.pattern(self.closers), file_content)

    def clauses_matches(self, file_content):
        return re.finditer(self.pattern(self.clauses), file_content)

    def pattern(self, els):
        return "\{\% (" + els + ")[^\%\}]* \%\}"

    def yield_blocks(self, file_content):
        # Assumes there's no blocks
        yield from [match.span() for match in re.finditer("\{\{ [^\}\}]* \}\}", file_content)]

    def raw_python_blocks(self, file_content):
        # Assumes there's no blocks
        yield from [match.span() for match in re.finditer("\{\{\{ [^\}\}\}]* \}\}\}", file_content)]

    def root_blocks(self, file_content):
        statement_by_start_index = []
        for occ in self.openners_matches(file_content):
            statement_by_start_index.append(("OPEN", occ))
        for occ in self.clauses_matches(file_content):
            statement_by_start_index.append(("CLAUSES", occ))
        for occ in self.closers_matches(file_content):
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

    def indent(self, block):
        __, stop = next(block)
        for iter_start, iter_stop in block:
           yield stop, iter_start
           stop = iter_stop

    def python_out_of_blocks(self, file_content, tab_level):
        file_content = file_content.replace("\\", "\\\\")
        file_content = file_content.replace("\n", "\\n")
        file_content = file_content.replace('"', '\\"')
        file_content = file_content.replace("'", "\\'")
        yield "    " * tab_level + f"yield \"{file_content}\"" + "\n"

    def python_inside_blocks(self, file_content, tab_level):
        start = 0
        for block_start, block_stop in self.yield_blocks(file_content):
            # yields before each blocks
            if file_content[start:block_start]:
                yield from self.python_out_of_blocks(file_content[start:block_start], tab_level)
            # yields blocks
            yield "    " * tab_level + "yield str(" + self.raw_python(file_content[block_start + 3:block_stop - 3], 0) + ")\n"
            start = block_stop
        # yields after last block (or everything, if there was no blocks), if empty
        if file_content == "":
            yield "    " * tab_level + "yield \"\"" # not pass, because if there's only pass, it's not a generator anymore
        # yields after last block, if non empty
        if file_content[start:]:
            yield from self.python_out_of_blocks(file_content[start:], tab_level)

    def python_without_statement_blocks(self, file_content, tab_level):
        start = 0
        for block_start, block_stop in self.raw_python_blocks(file_content):
            # yields before each blocks
            if file_content[start:block_start]:
                yield from self.python_inside_blocks(file_content[start:block_start], tab_level)
            # yields blocks
            yield self.raw_python(file_content[block_start + 4:block_stop - 4], tab_level + 1) + "\n"
            start = block_stop
        # yields after last block (or everything, if there was no blocks), if empty
        if file_content == "":
            yield "    " * tab_level + "yield \"\"" # not pass, because if there's only pass, it's not a generator anymore
        # yields after last block, if non empty
        if file_content[start:]:
            yield from self.python_inside_blocks(file_content[start:], tab_level)


    def raw_python(self, file_content, tab_level):
        return "    " * tab_level + file_content

    def full_python_texts_generator(self, file_content, tab_level=0):
        start = 0
        for block in self.root_blocks(file_content):
            # yields before each blocks
            if file_content[start:block[0][0]]:
                yield from self.python_without_statement_blocks(file_content[start:block[0][0]], tab_level)
            # yields blocks
            for ((block_start, block_stop), (indent_start, indent_stop)) in zip(block, self.indent(iter(block))):
                yield self.raw_python(file_content[block_start + 3:block_stop - 3], tab_level) + ":\n"
                yield from self.full_python_texts_generator(file_content[indent_start:indent_stop], tab_level=tab_level + 1)
            start = block[-1][-1]
        # yields after last block (or everything, if there was no blocks), if empty
        if file_content == "":
            yield "    " * tab_level + "yield \"\"" # not pass, because if there's only pass, it's not a generator anymore
        # yields after last block, if non empty
        if file_content[start:]:
            yield from self.python_without_statement_blocks(file_content[start:], tab_level)

    def python_code(self, file_content):
        return "def easter_egg():\n" + "".join(self.full_python_texts_generator(file_content, tab_level=1)) + "\nres = \"\".join(easter_egg())"

def render(file_content, *args, **kwargs):
    snek = Parser().python_code(file_content)
    globals().update(kwargs)
    exec(snek, globals())
    return res
