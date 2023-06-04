import re
x


CONTROL_PATTERN_START = "{%"
CONTROL_PATTERN_STOP = "%}"
YIELDED_PATTERN_START = "{{"
YIELDED_PATTERN_STOP = "}}"
RAW_PATTERN_START = "{{{"
RAW_PATTERN_STOP = "}}}"


class Parser:
    def __init__(self):
        self.control_flows = {
            "if": ["elif", "else"],
            "for": ["else"],
            "try": ["except", "else", "finally"],
            "with": [],
        }
        self.openners = "|".join(self.control_flows.keys())
        self.closers = "|".join(["end" + key for key in self.control_flows.keys()])
        self.clauses = "|".join(["|".join(value) for value in self.control_flows.values() if value])

    def openners_matches(self, file_content):
        return re.finditer(self.pattern(self.openners), file_content)

    def closers_matches(self, file_content):
        return re.finditer(self.pattern(self.closers), file_content)

    def clauses_matches(self, file_content):
        return re.finditer(self.pattern(self.clauses), file_content)

    def remove_surrounding_markers(self, pattern_start, pattern_stop, file_content):
        return file_content[len(pattern_start) + 1:-(len(pattern_stop) + 1)] # +1 for space (no, not you elon)

    def remove_control_flow_markers(self, file_content):
        return self.remove_surrounding_markers(CONTROL_PATTERN_START, CONTROL_PATTERN_STOP, file_content)

    def remove_control_flow_end_markers(self, file_content):
        return self.remove_surrounding_markers(CONTROL_PATTERN_START, CONTROL_PATTERN_STOP, file_content)[3:] # removes "end"

    def remove_yielded_block_markers(self, file_content):
        return self.remove_surrounding_markers(YIELDED_PATTERN_START, YIELDED_PATTERN_STOP, file_content)

    def remove_raw_block_markers(self, file_content):
        return self.remove_surrounding_markers(RAW_PATTERN_START, RAW_PATTERN_STOP, file_content)

    def pattern(self, els):
        return CONTROL_PATTERN_START + " (" + els + ").*? " + CONTROL_PATTERN_STOP

    def yield_blocks(self, file_content):
        # Assumes there's no blocks
        yield from [match.span() for match in re.finditer(YIELDED_PATTERN_START + " .*? " + YIELDED_PATTERN_STOP, file_content)]

    def raw_python_blocks(self, file_content):
        # Assumes there's no blocks
        yield from [match.span() for match in re.finditer(RAW_PATTERN_START + " .*? " + RAW_PATTERN_STOP, file_content)]

    def control_blocks(self, file_content):
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
                if statement == "CLAUSE":
                    continue # found a clause
                if statement == "END":
                    unopened_end = self.remove_control_flow_end_markers(file_content[match.start():])
                    raise ValueError(f"statement {unopened_end} closed but never opened.")
                block.append(match.span())
                open_counter = 0 # if facing open statement, we enter block
                continue
            if open_counter == 0: # inside open block, but not inside any nested block
                if statement == "END":
                    block.append(match.span())
                    control_flow_oppenner = file_content[block[0][0]:block[0][1]]
                    statement_name = self.remove_control_flow_markers(control_flow_oppenner).split(' ')[0]
                    control_flow_ender = file_content[block[-1][0]:block[-1][1]]
                    ended_statement_name = self.remove_control_flow_end_markers(control_flow_ender)
                    if statement_name != ended_statement_name:
                        raise ValueError(f"statement {statement_name} closed by {ended_statement_name} closer.")

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
        if block: # block opened, but never closed
            control_flow_oppenner = file_content[block[0][0]:block[0][1]]
            unclosed_statement = self.remove_control_flow_markers(control_flow_oppenner).split(' ')[0]
            raise ValueError(f"statement {unclosed_statement} opened but never closed.")

    def python_out_of_blocks(self, file_content, tab_level):
        file_content = file_content.replace("\\", "\\\\")
        file_content = file_content.replace("\n", "\\n")
        file_content = file_content.replace('"', '\\"')
        file_content = file_content.replace("'", "\\'")
        yield "    " * tab_level + f"yield \"{file_content}\"" + "\n"

    def python_without_statement_and_raw(self, file_content, tab_level):
        start = 0
        for block_start, block_stop in self.yield_blocks(file_content):
            # yields before each blocks
            if file_content[start:block_start]:
                yield from self.python_out_of_blocks(file_content[start:block_start], tab_level)
            # yields blocks
            yielded_block = self.remove_yielded_block_markers(file_content[block_start:block_stop])
            yield "    " * tab_level + "yield str(" + self.raw_python(yielded_block, 0) + ")\n"
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
                yield from self.python_without_statement_and_raw(file_content[start:block_start], tab_level)
            # yields blocks
            raw_block = self.remove_raw_block_markers(file_content[block_start:block_stop])
            yield self.raw_python(raw_block, tab_level) + "\n"
            start = block_stop
        # yields after last block (or everything, if there was no blocks), if empty
        if file_content == "":
            yield "    " * tab_level + "yield \"\"" # not pass, because if there's only pass, it's not a generator anymore
        # yields after last block, if non empty
        if file_content[start:]:
            yield from self.python_without_statement_and_raw(file_content[start:], tab_level)


    def raw_python(self, file_content, tab_level):
        return "    " * tab_level + file_content

    def indent(self, block):
        __, stop = next(block)
        for iter_start, iter_stop in block:
           yield stop, iter_start
           stop = iter_stop

    def full_python_texts_generator(self, file_content, tab_level=0):
        start = 0
        for block in self.control_blocks(file_content):
            # yields before each control flow blocks
            if file_content[start:block[0][0]]:
                yield from self.python_without_statement_blocks(file_content[start:block[0][0]], tab_level)
            # yields blocks itself, and the actual control flow statement
            for ((block_start, block_stop), (indent_start, indent_stop)) in zip(block, self.indent(iter(block))):
                control_flow = self.remove_control_flow_markers(file_content[block_start:block_stop])
                yield self.raw_python(control_flow, tab_level) + ":\n"
                yield from self.full_python_texts_generator(file_content[indent_start:indent_stop], tab_level=tab_level + 1)
            start = block[-1][-1]
        # yields after last block (or everything, if there was no blocks), if file_content is empty
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
