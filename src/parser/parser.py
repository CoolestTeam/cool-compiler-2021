import ply.yacc as yacc
from nodes import *
from lexer import MyLexer
import sys

class MyParser():
    def __init__(self):
        self.build()

    # Build the parser
    def build(self, **kwargs):
        self.lexer = MyLexer()
        self.tokens = self.lexer.tokens
        self.errors = []
        self.parser = yacc.yacc(module=self)

    def parse(self, _cool_program):
        return self.parser.parse(_cool_program)
    
    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT')
        ('nonassoc', 'LESS', 'LESSEQ', 'EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'NOX'),
        ('right', 'ARROBA'),
        ('right', 'DOT')
    )


if __name__ == "__main__":
    _file = sys.argv[1]
    _cool_program = open(_file, encoding="utf-8").read()

    _myparser = MyParser()
    _myparse_result = _myparser.parse(_cool_program)

    if _myparser.errors:
        print(_myparser.errors[0])