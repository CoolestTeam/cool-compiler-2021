from semantic.tools.type import String_Type, Int_Type, Object_Type, Bool_Type, Auto_Type, IO_Type, Error_Type
from semantic.tools.context import Context
from semantic.tools.error import SemanticError
from nodes.ast_nodes import ProgramNode, ClassNode
from .visitor import *


class TypeCollector(object):
    def __init__(self, errors=[]):
        self.context = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        self.context = Context()
        self.context.types['Object'] = Object_Type()
        self.context.types['String'] = String_Type()
        self.context.types['Int'] = Int_Type()
        self.context.types['Bool'] = Bool_Type()
        self.context.types['AUTO_TYPE'] = Auto_Type()
        self.context.types['IO'] = IO_Type()
        self.context.types['Error'] = Error_Type()
        self.context.create_type('SELF_TYPE')

        #definir los metodos por defecto de las clases basicas
        
        #Object_Type -> abort(): Object_Type
        self.context.types['Object'].define_method('abort', [], [], Object_Type())

        #Object_Type -> type_name():String_Type
        self.context.types['Object'].define_method('type_name', [], [], String_Type())

        #Object_Type -> copy():SELF_TYPE
        self.context.types['Object'].define_method('copy', [], [], self.context.types['SELF_TYPE'])

        #String_Type -> length():Int_Type
        self.context.types['String'].define_method('length', [], [], Int_Type())

        #String_Type -> concat(s: String_Type):String_Type
        self.context.types['String'].define_method('concat', ['s'], [String_Type()], String_Type())

        #String_Type -> substr(i: Int_Type, j: Int_Type):String_Type
        self.context.types['String'].define_method('substr', ['i', 'j'], [Int_Type(), Int_Type()], String_Type())

        #IO_Type -> out_string(x: String_Type):SELF_TYPE
        self.context.types['IO'].define_method('out_string', ['x'], [String_Type()], self.context.types['SELF_TYPE'])

        #IO_Type -> out_int(x: Int_Type):SELF_TYPE
        self.context.types['IO'].define_method('out_int', ['x'], [Int_Type()], self.context.types['SELF_TYPE'])
        
        #IO_Type -> in_string():String_Type
        self.context.types['IO'].define_method('in_string', [], [], String_Type())

        #IO_Type -> in_int():Int_Type
        self.context.types['IO'].define_method('in_int', [], [], Int_Type())
        
        
        for dec in node.classes:
            self.visit(dec)

    @visitor.when(ClassNode)
    def visit(self, node):
        try:
            self.context.create_type(node.name)
        except SemanticError as e:
            self.errors.append(e.text)