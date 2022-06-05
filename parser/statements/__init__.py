

class Statement:
    def __init__(self, statement_str, expressionless=False, clauses=None, expressionless_clauses=None, repeatable_clauses=None, optional_clauses=None):
        self.statement_str = statement_str
        self.expressionless = expressionless
        if clauses is None:
            self.clauses = []
        else:
            self.clauses = clauses
        if repeatable_clauses is None:
            self.repeatable_clauses = []
        else:
            self.repeatable_clauses = repeatable_clauses
        if expressionless_clauses is None:
            self.expressionless_clauses = []
        else:
            self.expressionless_clauses = expressionless_clauses
        if optional_clauses is None:
            self.optional_clauses = []
        else:
            self.optional_clauses = optional_clauses

    def pattern(self):
        statement_pattern = self.statement(self.statement_str, expressionless=self.expressionless)
        clause_pattern = "".join(self.clause(clause) for clause in self.clauses)
        endstatement_pattern = self.end_statement(self.statement_str)
        return statement_pattern + clause_pattern + endstatement_pattern

    def statement(self, statement, expressionless=False):
        if expressionless:
            expression = ""
        else:
            expression =  "(?P<" + statement + "expression>[^(\%\})]*)"
        return "\{\% " + statement + expression + " \%\}(?P<" + statement + "block>[^(\{\%)]*)"

    def clause(self, clause):
        if clause in self.repeatable_clauses:
            if clause in self.optional_clauses:
                repeater = "*"
            else:
                repeater = "+"
        else:
            if clause in self.optional_clauses:
                repeater = "?"
            else:
                repeater = ""
        clause_pattern = self.statement(clause, expressionless=clause in self.expressionless_clauses)
        return f"(?P<{clause}s>({clause_pattern}){repeater})"

    def repeatable_clause(self, clause):
        clause_pattern = self.statement(clause)
        return f"(?P<{clause}s>({clause_pattern})*)"

    def optional_clause(self, clause):
        clause_pattern = self.statement(clause, expressionless=True)
        return f"({clause_pattern})?"

    def end_statement(self, statement):
        return "\{\% end" + statement + " \%\}"
