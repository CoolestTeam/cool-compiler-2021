from .visitor import *
from nodes import *
from .var_collector import scope_find
from .type_checker import child_scope_find

class SelfTypeVisitor(object):
    def __init__(self, context, errors=[]):
        self.context =  context
        self.errors = errors
        self.current_type = None
        self.current_method = None
        self.scope_object = None

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope):
        self.scope_object = scope
        for declaration in node.classes:
            self.visit(declaration, scope)

    @visitor.when(ClassNode)
    def visit(self, node, scope):
        try:
            new_scope = scope.childrens_dict[node.name]
        except KeyError:
            new_scope = scope_find(scope, node.name)

        if new_scope == None: return

        self.current_type = self.context.get_type(node.name)

        fd = [feat for feat in node.features if isinstance(feat, ClassMethodNode)]

        for feat in node.features:
            if isinstance(feat, AttrInitNode) or isinstance(feat, AttrDefNode):
                self.visit(feat, new_scope)
            else:
                self.visit(feat, new_scope.childrens_dict[feat.name])    


    @visitor.when(AttrInitNode)
    def visit(self, node, scope):
        vinfo = scope.find_variable(node.name)
        if node.attr_type == 'SELF_TYPE':
            vinfo.type = self.current_type


    @visitor.when(AttrDefNode)
    def visit(self, node, scope):
        vinfo = scope.find_variable(node.name)
        if node.attr_type == 'SELF_TYPE':
            vinfo.type = self.current_type


    @visitor.when(ClassMethodNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.name)

        for param in node.params:
            self.visit(param, scope)

        if node.type.lex == 'SELF_TYPE':
            self.current_method.return_type = self.current_type 
            
        self.visit(node.expression, scope)


    @visitor.when(FormalParamNode)
    def visit(self, node, scope):

        pname = node.name
        ptype = node.param_type
        if ptype == 'SELF_TYPE':
            varinfo = scope.find_variable(pname)
            varinfo.type = self.current_type

            self.current_type.change_type(self.current_method, pname, self.current_type)


    @visitor.when(LetInitNode)
    def visit(self, node, scope):
        varinfo = scope.find_variable(node.name)

        if node.let_type == 'SELF_TYPE':
            varinfo.type = self.current_type


    @visitor.when(LetDefNode)
    def visit(self, node, scope):
        varinfo = scope.find_variable(node.name)

        if node.let_type == 'SELF_TYPE':
            varinfo.type = self.current_type


    @visitor.when(AssignNode)
    def visit(self, node, scope):
        varinfo = scope.find_variable(node.name)

        if varinfo.type.name == 'SELF_TYPE':
            varinfo.type = self.current_type


    @visitor.when(BlockNode)
    def visit(self, node, scope):
        for exp in node.expr_list:
            self.visit(exp, scope)


    @visitor.when(LetNode)
    def visit(self, node, scope):
        try:
            child_scope = scope.childrens_let_dict[node]
        except:
            child_scope = scope

        for init in node.init_list:
            self.visit(init, child_scope)
        self.visit(node.body, child_scope)

    @visitor.when(CaseNode) 
    def visit(self, node, scope):
        self.visit(node.expression, scope)
        new_scope = scope.childrens_case_dict[node]

        for case in node.act_list:
            new_n_scope = new_scope.childrens_case_dict[case]
            self.visit(case, new_n_scope)
        

    @visitor.when(ActionNode)
    def visit(self, node, scope):
        var_info = scope.find_variable(node.name)
        self.visit(node.body, scope)

        if var_info.type.name == 'SELF_TYPE':
            var_info.type = self.current_type