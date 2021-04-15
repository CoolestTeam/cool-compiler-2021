import ply.lex as lex
import sys

class MyLexer():
    def __init__(self):
        self.build()

    # The tokens list
    def get_basic_tok(self):
        return [
            "INTEGER",
            "STRING",
            "BOOLEAN",
            "PLUS",
            "MINUS",
            "MULTIPLY",
            "DIVIDE",
            "EQUAL",
            "LESS",
            "LESSEQ",
            "ASSIGN",
            "NOX",
            "ID",
            "TYPE",
            "LPAREN",
            "RPAREN",
            "LBRACE",
            "RBRACE",
            "COLON",
            "SEMIC",
            "COMMA",
            "DOT",
            "ARROBA",
            "ARROW"
        ]

    def get_reserved_keywds(self):
        return {
            "class": "CLASS",
            "case": "CASE",
            "esac": "ESAC",
            "let": "LET",
            "in": "IN",
            "inherits": "INHERITS",
            "isvoid": "ISVOID",
            "new": "NEW",
            "if": "IF",
            "else": "ELSE",
            "then": "THEN",
            "fi": "FI",
            "while": "WHILE",
            "loop": "LOOP",
            "pool": "POOL",
            "true": "TRUE",
            "false": "FALSE",
            "not": "NOT",
            "of": "OF",
            "Object": "OBJECT_TYPE",
            "Int": "INT_TYPE",
            "String": "STRING_TYPE",
            "Bool": "BOOL_TYPE",
            "SELF_TYPE": "SELF_TYPE",
            "Main": "MAIN_TYPE",
            "IO": "IO_TYPE"
        }

    # Build the lexer
    def build(self, **kwargs):
        self.tokens = self.get_basic_tok() + list(self.get_reserved_keywds.values())
        self.reserved = list(self.get_reserved_keywds.values())
        self.lexer = lex.lex(module=self, **kwargs)



if __name__ == "__main__":
    _file = sys.argv[1]
    _cool_program = open(_file, encoding="utf-8").read()

    _mylexer = MyLexer()
    _mylexer.lexer.input(_cool_program)

    for tok in _mylexer:
        pass
