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

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)



if __name__ == "__main__":
    _file = sys.argv[1]
    _cool_program = open(_file, encoding="utf-8").read()

    _mylexer = MyLexer()
    _mylexer.lexer.input(_cool_program)

    for tok in _mylexer:
        pass
