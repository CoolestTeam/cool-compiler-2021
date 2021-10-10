from semantic.tools.error import SemanticError, circular_dependency_, incompatible_types_
from semantic.tools.type import Type, Error_Type
from nodes.ast_nodes import ProgramNode, ClassNode, ClassMethodNode, AttrInitNode, AttrDefNode
from .visitor import *


class TypeBuilder:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.errors = errors
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ProgramNode)
    def visit(self, node):
        for dec in node.classes:
            self.visit(dec)
    
    @visitor.when(ClassNode)
    def visit(self, node):
        try:
            self.current_type = self.context.get_type(node.name)
            
        except SemanticError as e:
            self.current_type = Error_Type()
            self.errors.append(e.text)
            
        if node.parent is not None:
            try:
                parent = self.context.get_type(node.parent.name)
                
                if parent.name == 'String' or parent.name == 'Int' or parent.name == 'Bool':
                    raise SemanticError(incompatible_types_ %(node.name, parent.name))
                current = parent
                while current is not None:
                    if current.name == self.current_type.name:
                        raise SemanticError(circular_dependency_ %(parent.name, self.current_type.name))
                    current = current.parent

            except SemanticError as e:
                parent = Error_Type()
                self.errors.append(e.text)
            
            self.current_type.set_parent(parent)

        for feature in node.features:
            self.visit(feature)

        if node.name == 'Main':
            try:
                meth = self.current_type.get_method('main')
            except SemanticError:
                self.errors.append('Method main not exist')
    

    @visitor.when(ClassMethodNode)
    def visit(self, node):
        args_names = []
        args_types = []
        for param in node.params:
            try:
                name = param.name
                type_ = param.param_type
                args_names.append(name)
                args_types.append(self.context.get_type(type_))
            except SemanticError as e:    
                args_types.append(Error_Type())
                self.errors.append(e.text)
        
        try:
            return_type = self.context.get_type(node.return_type)
        except SemanticError as e:
            return_type = Error_Type()
            self.errors.append(e.text)
    
        try:
            self.current_type.define_method(node.name, args_names, args_types, return_type)
        except SemanticError as e:
            self.errors.append(e.text)

    
    @visitor.when(AttrInitNode)
    def visit(self, node):
        try:
            attr_type = self.context.get_type(node.attr_type)
        except SemanticError as e:
            attr_type = Error_Type()
            self.errors.append(e.text)
        
        try:
            self.current_type.define_attribute(node.name, attr_type)
        except SemanticError as e:
            self.errors.append(e.text)

    
    @visitor.when(AttrDefNode)
    def visit(self, node):
        try:
            attr_type = self.context.get_type(node.attr_type)
        except SemanticError as e:
            attr_type = Error_Type()
            self.errors.append(e.text)
        
        try:
            self.current_type.define_attribute(node.name, attr_type)
        except SemanticError as e:
            self.errors.append(e.text)