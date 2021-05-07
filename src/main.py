from lexer import MyLexer
from parser import MyParser
import sys

if __name__ == "__main__":

    _mylexer = MyLexer()
    _myparser = MyParser()

    if len(sys.argv) > 1:
        _file = sys.argv[1]
        _cool_program = open(_file, encoding="utf-8").read()
        try:
            _mylexer_result = _mylexer.tokenize(_cool_program)
        except:
            pass
        
        if _mylexer.errors:
            print(_mylexer.errors[0])
            exit(1)
        try:
            _myparse_result = _myparser.parse(_cool_program)
        except:
            pass
        # _myparse_result = _myparser.parse(_cool_program)

        if _myparser.errors:
            print(_myparser.errors[0])
            exit(1)
