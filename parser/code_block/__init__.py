import re


class Statement:
    def __init__(self, python_formatted_string, name, expressionless=False):
        self.python_formatted_string = python_formatted_string
        self.name = name
        self.expressionless = expressionless

    def pattern(self):
        return self.statement_pattern() + self.block_pattern()

    def statement_pattern(self):
        if self.expressionless:
            expression = ""
        else:
            expression =  "(?P<" + self.name + "expression>[^\%\}]*)"
        return "\{\% " + self.name + expression + " \%\}"

    def block_pattern(self):
        return "(?P<" + self.name + "block>[^\{\%]*)"

    def end_pattern(self):
        return "\{\% end" + self.name + " \%\}"

    def python_statement(self, statement_text):
        return statement_text[3:-3] + ":"

    def python_block(self, block_text):
        return f"    res += \"{block_text}\""

    def python_parsed(self, statement_text, block_text):
        return self.python_statement(statement_text) + "\n" + self.python_block(block_text)

    def python_str(self, match):
        return self.python_formatted_string.format(**match.groupdict())

class Clause(Statement):
    def __init__(self, python_formatted_string, name, expressionless=False, repeatable=False, optional=False):
        self.python_formatted_string = python_formatted_string
        self.name = name
        self.expressionless = expressionless
        self.repeatable = repeatable
        self.optional = optional

    def grouped_pattern(self):
        if self.repeatable:
            if self.optional:
                repeater = "*"
            else:
                repeater = "+"
        else:
            if self.optional:
                repeater = "?"
            else:
                repeater = ""
        clause_pattern = self.pattern()
        return f"(?P<{self.group_name()}>({clause_pattern}){repeater})"

    def group_name(self):
        clause_group_name = f"{self.name}"
        if self.repeatable:
            clause_group_name = f"{clause_group_name}s"
        return clause_group_name

    def python_str(self, match):
        python_str = ""
        if match.group(self.group_name()):
            for res_elif in re.finditer(self.pattern(), match.group(self.group_name())):
                python_str += self.python_formatted_string.format(
                    **res_elif.groupdict()
                )
        return python_str

class CodeBlock:
    def __init__(self, statement, clause_list=None):
        self.statement = statement
        if clause_list is None:
            self.clause_list = []
        else:
            self.clause_list = clause_list

    def pattern(self):
        statement_pattern = self.statement.pattern()
        clause_pattern = "".join(clause.grouped_pattern() for clause in self.clause_list)
        endstatement_pattern = self.statement.end_pattern()
        return statement_pattern + clause_pattern + endstatement_pattern
    
    def pattern_by_start_index(self, file_content, pattern):
        return list(re.finditer(pattern, file_content))

    def sorted_pattern(self, file_content, pattern):
        return sorted(self.pattern_by_start_index(file_content, pattern), key=lambda x: x.start())

    def list_all_matches(self, file_content):
        statement_by_start_index = []
        for occ in self.pattern_by_start_index(file_content, self.statement.statement_pattern()):
            statement_by_start_index.append((self.statement, occ))
        for clause in self.clause_list:
            for occ in self.pattern_by_start_index(file_content, clause.statement_pattern()):
                statement_by_start_index.append((clause, occ))
        for occ in self.pattern_by_start_index(file_content, self.statement.end_pattern()):
            statement_by_start_index.append(("END", occ))
        
        statement_by_start_index = sorted(statement_by_start_index, key=lambda x: x[1].start())
        open_counter = None
        block = []
        for statement, match in statement_by_start_index:
            if open_counter is None: # outside any blocks
                if statement is not self.statement:
                    continue
                block.append((statement, match))
                open_counter = 0 # if facing open statement, we enter block
                continue
            if open_counter == 0: # inside open block, but not inside any nested block
                if statement == "END":
                    block.append((statement, match))
                    yield block
                    block = []
                    open_counter = None
                    continue
                if statement is not self.statement:
                    block.append((statement, match))
                    continue
            # no matter if nested or not, but we are in open block
            if statement is self.statement:
                open_counter += 1
            if statement == "END":
                open_counter -= 1

    def python_str(self, match):
        res = self.statement.python_str(match)
        for clause in self.clause_list:
            res += clause.python_str(match)
        return res

    def replacement(self, match):
        exec(self.python_str(match), globals())
        return res

    def all_replacement(self, text):
        for match in re.finditer(self.pattern(), text):
            start, stop = match.span()
            yield text[start:stop], self.replacement(match)
