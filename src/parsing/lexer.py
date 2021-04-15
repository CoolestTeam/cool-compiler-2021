import ply.lex as lex
import sys

class MyLexer():
    def __init__(self):
        self.build()

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
