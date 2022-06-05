class Statement:
    def __init__(self, name, expressionless=False):
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

class Clause(Statement):
    def __init__(self, name, expressionless=False, repeatable=False, optional=False):
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
        clause_pattern = super().pattern()
        clause_group_name = f"{self.name}"
        if self.repeatable:
            clause_group_name = f"{clause_group_name}s"
        return f"(?P<{clause_group_name}>({clause_pattern}){repeater})"

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
