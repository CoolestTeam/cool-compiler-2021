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
            "of": "OF"
        }

    def get_builtin_types(self):
        return {
            "Object": "OBJECT_TYPE",
            "Int": "INT_TYPE",
            "String": "STRING_TYPE",
            "Bool": "BOOL_TYPE",
            "SELF_TYPE": "SELF_TYPE",
            "Main": "MAIN_TYPE",
            "IO": "IO_TYPE"
        }

    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_EQUAL = r'\='
    t_LESS = r'\<'
    t_LESSEQ = r'\<\='
    t_ASSIGN = r'\<\-'
    t_NOX = r'~'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COLON = r'\:'
    t_SEMIC = r'\;'
    t_COMMA = r'\,'
    t_DOT = r'\.'
    t_ARROBA = r'\@'
    t_ARROW = r'\=\>'
    t_ignore = ' \t\r\f'
    t_ignore_LINE_COMMENT = r"\-\-[^\n]*"

    # Regular expression rules with some action code
    def t_INTEGER(self, tok):
        tok.value = int(tok.value)
        return tok

    def t_ID(self, tok):
        if self.get_reserved_keywds.__contains__(str.lower(tok.value)):
            tok.value = str.lower(tok.value)
            tok.type = self.get_reserved_keywds[str.lower(tok.value)]
        else:
            tok.type = "ID"
        return tok

    def t_TYPE(self, tok):
        if self.get_reserved_keywds.__contains__(str.lower(tok.value)):
            tok.value = str.lower(tok.value)
            tok.type = self.get_reserved_keywds[str.lower(tok.value)]
        else:
            tok.type = "TYPE"
        return tok
    
    def t_newline(self, tok):
        tok.lexer.lineno += len(tok.value)

    # Build the lexer
    def build(self, **kwargs):
        self.tokens = self.get_basic_tok() + list(self.get_reserved_keywds.values()) + list(self.get_builtin_types.values())
        self.reserved = list(self.get_reserved_keywds.values()) + + list(self.get_builtin_types.values())
        self.lexer = lex.lex(module=self, **kwargs)



if __name__ == "__main__":
    _file = sys.argv[1]
    _cool_program = open(_file, encoding="utf-8").read()

    _mylexer = MyLexer()
    _mylexer.lexer.input(_cool_program)

    for tok in _mylexer:
        pass
