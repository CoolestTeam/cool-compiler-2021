import itertools as itt
from .type import Type, Void_Type
from .error import SemanticError

class Context:
    def __init__(self):
        self.types = {}

    def create_type(self, name:str, isvoid = False):
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        typex = self.types[name] = Void_Type(name) if isvoid else Type(name)
        return typex

    def get_type(self, name:str):
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def __str__(self):
        return '\n\t\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n'

    def __repr__(self):
        return str(self)