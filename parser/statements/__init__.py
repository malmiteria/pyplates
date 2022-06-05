import re


class Statement:
    def __init__(self, python_formatted_string, name, expressionless=False):
        self.python_formatted_string = python_formatted_string
        self.name = name
        self.expressionless = expressionless

    def pattern(self):
        if self.expressionless:
            expression = ""
        else:
            expression =  "(?P<" + self.name + "expression>[^\%\}]*)"
        return "\{\% " + self.name + expression + " \%\}(?P<" + self.name + "block>[^\{\%]*)"

    def end_pattern(self):
        return "\{\% end" + self.name + " \%\}"

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

    def python_str(self, match):
        res = self.statement.python_str(match)
        for clause in self.clause_list:
            res += clause.python_str(match)
        return res
