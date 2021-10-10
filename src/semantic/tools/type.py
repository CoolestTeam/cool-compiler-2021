import itertools as itt
from .error import SemanticError
from .attribute import Attribute
from .methods import Method

class Type:
    def __init__(self, name:str):
        if name == 'ObjectType':
            return Object_Type()
        self.name = name
        self.attributes = []
        self.methods = {}
        self.parent = Object_Type()

    def set_parent(self, parent):
        if self.parent != Object_Type() and self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

    def get_attribute(self, name:str):
        for attr in self.attributes:
            if attr.name == name: return attr

        if self.parent is None:
            raise SemanticError(f'Attribute {name} is not defined in {self.name}')
        try:
            return self.parent.get_attribute(name)
        except SemanticError:
            raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')

    def define_attribute(self, name:str, typex):
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name:str):
        try:
            return self.methods[name]
        except KeyError:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name:str, param_names:list, param_types:list, return_type):
        if name in self.methods:
            raise SemanticError(f'Method "{name}" already defined in {self.name}')
        method = self.methods[name] = Method(name, param_names, param_types, return_type)
        return method

    def change_type(self, method, n_param, newtype):
        idx = method.param_names.index(n_param)
        method.param_types[idx] = newtype                

    def conforms_to(self, other):
        return other.bypass() or self == other or self.parent is not None and self.parent.conforms_to(other)

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        output += '' if self.parent is None else f' : {self.parent.name}'
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods.values())
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)


class Object_Type(Type):
    def __init__(self):
        self.name = 'Object'
        self.attributes = []
        self.methods = {}
        self.parent = None
    
    def conforms_to(self, other):
        return True

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Object_Type)

    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, Object_Type)


class Error_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, '<error>')

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Error_Type)

    def __ne__(self, other):
        return not isinstance(other, Error_Type)



class Void_Type(Object_Type):
    def __init__(self, name:str):
        Type.__init__(self, name)

    def conforms_to(self, other):
        raise Exception('Invalid type: void type.')

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Void_Type)



class Bool_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, 'Bool')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Bool_Type)
    
    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, Bool_Type)



class Int_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, 'Int')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Int_Type)

    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, Int_Type)



class String_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, 'String')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, String_Type)

    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, String_Type)



class Auto_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, 'AUTO_TYPE')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, Auto_Type)

    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, Auto_Type)


class IO_Type(Object_Type):
    def __init__(self):
        Type.__init__(self, 'IO')

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, IO_Type)

    def __ne__(self, other):
        return other.name != self.name and not isinstance(other, IO_Type)