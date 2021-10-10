from semantic.tools.error import read_only_, local_already_defined_, var_not_defined_, SemanticError
from semantic.tools.scope import Scope
from semantic.tools.type import Error_Type
from nodes import *
from .visitor import *

class VarCollector:
    def __init__(self, context, errors=[]):
        self.context = context
        self.scope_object = None
        self.current_type = None
        self.current_method = None
        self.errors = errors
        self.str_a_case = None

    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope=None):
        scope = Scope('Object')
        scope.is_class = True
        self.scope_replet(scope)
        scope.define_variable('self', self.current_type)

        for item in ['Bool', 'Int', 'IO', 'String']:
            new_scope = scope.create_child(item)
            new_scope.is_class = True
            self.scope_replet(new_scope)
            new_scope.define_variable('self', self._get_type(item))

        self.scope_object = scope

        for declaration in node.classes:    
            new_parent_scope = scope
            if declaration.parent != None:
                p_scope = scope_find(self.scope_object, declaration.parent)
                if p_scope == None:
                    p_scope = self.scope_create(self.scope_object, declaration.parent)
                
                new_parent_scope = p_scope

            new_scope = scope_find(self.scope_object, declaration.name)
            if new_scope != None:
                old_parent = new_scope.parent
                old_parent.children_scope_class_delete(new_scope.name)
                new_parent_scope.add_child(new_scope)
            else: 
                new_scope = new_parent_scope.create_child(declaration.name)
                new_scope.define_variable('self', self.current_type)
                self.scope_replet(new_scope)

            new_scope.is_class = True

        #recorrido preorden de las declaraciones
        preorden = self.pre_order_class_walk(self.scope_object)
        for scp in preorden:
            dec = self.declaration_find(scp.name, node.classes)
            if dec == None: continue
            self.visit(dec, scp)
        return scope

    @visitor.when(ClassNode)
    def visit(self, node, scope):
        self.current_type = self._get_type(node.name)  
        
        for feat in node.features:
            if isinstance(feat, AttrInitNode):
                self.visit(feat, scope)
            elif isinstance(feat, AttrDefNode):
                self.visit(feat, scope)

        for feat in node.features:
            if isinstance(feat, ClassMethodNode):
                self.visit(feat, scope)


    @visitor.when(AttrDefNode)
    def visit(self, node, scope):
        scope.define_attribute(self.current_type.get_attribute(node.name))


    @visitor.when(AttrInitNode)
    def visit(self, node, scope):
        scope.define_attribute(self.current_type.get_attribute(node.name))
        
        self.str_a_case = node.name
        self.visit(node.expression, scope)
        self.str_a_case = None

        
    @visitor.when(ClassMethodNode)
    def visit(self, node, scope):

        parent = self.current_type.parent.name
        self.current_method = self.current_type.get_method(node.name)

        new_scope = scope.create_child(node.name)
        scope.func_dict[node.name] = new_scope

        for param in node.params:
            self.visit(param, new_scope)

        self.visit(node.expression, new_scope)


    @visitor.when(FormalParamNode)
    def visit(self, node, scope):

        pname = node.name
        ptype = node.param_type
        scope.define_variable(pname, self._get_type(ptype))


    @visitor.when(LetDefNode)
    def visit(self, node, scope):
        if node.name == 'self':
            self.errors.append(read_only_)
            return

        if scope.is_defined_local(node.name):
            var = scope.find_variable(node.name)
            type_ = self._get_type(node.let_type)  
            if type_ != var.type:
                var.type = type_     
            if len(scope.name) > 2 and scope.name[:3] != 'let':
                self.errors.append(local_already_defined_ %(node.name, scope.name)) 

            return

        vtype = self._get_type(node.let_type)

        var_info = scope.define_variable(node.name, vtype)


    @visitor.when(LetInitNode)
    def visit(self, node, scope):
        if node.name == 'self':
            self.errors.append(read_only_)
            return

        if scope.is_defined_local(node.name):
            var = scope.find_variable(node.name)
            type_ = self._get_type(node.let_type)  
            if type_ != var.type:
                var.type = type_     
            if len(scope.name) > 2 and scope.name[:3] != 'let':
                self.errors.append(local_already_defined_ %(node.name, scope.name)) 

            return

        vtype = self._get_type(node.let_type)

        var_info = scope.define_variable(node.name, vtype)
       
        self.visit(node.expression, scope)

        
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        if node.name == 'self':
            self.errors.append(read_only_)
            
        vinfo = scope.find_variable(node.name)
        if vinfo is None:
            self.errors.append(var_not_defined_ %(node.name, self.current_method.name))
            vtype = Error_Type()
            scope.define_variable(node.name, vtype)
        else:
            try:
                vtype = vinfo.type
            except AttributeError:
                vtype = vinfo
            
        self.visit(node.expression, scope)
    
    @visitor.when(BlockNode)
    def visit(self, node, scope):
        for exp in node.expr_list:
            self.visit(exp, scope)


    @visitor.when(LetNode)
    def visit(self, node, scope):
        str_let = self.find_lets(scope)
        
        new_scope = scope.create_child(str_let + ' ' + scope.name)

        scope.childrens_let_dict[node] = new_scope

        for init in node.init_list:
            self.visit(init, new_scope)
        
        self.visit(node.body, new_scope)

    @visitor.when(BinaryOpNode)
    def visit(self, node, scope):
        self.visit(node.left, scope)
        self.visit(node.right, scope)
    
    @visitor.when(UnaryOpNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope)

    @visitor.when(IdNode)
    def visit(self, node, scope):
        if not scope.is_defined(node.name):
            self.errors.append(var_not_defined_ %(node.name, self.current_method.name))
            vinfo = scope.define_variable(node.name, Error_Type())
        else:
            vinfo = scope.find_variable(node.name)
        return vinfo

    @visitor.when(WhileNode)
    def visit(self, node, scope):
        self.visit(node.predicate, scope)
        self.visit(node.expression, scope)

    @visitor.when(IfNode)
    def visit(self, node, scope):
        self.visit(node.predicate, scope)
        self.visit(node.then_expr, scope)
        self.visit(node.else_expr, scope)

    @visitor.when(IsVoidNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope)
    
    @visitor.when(DynamicCallNode)
    def visit(self, node, scope):
        self.visit(node.obj, scope)
        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(StaticCallNode)
    def visit(self, node, scope):
        self.visit(node.obj, scope)
        for arg in node.args:
            self.visit(arg, scope)

    @visitor.when(CaseNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope)

        str_case = self.find_cases(scope)

        if self.str_a_case != None:
            str_case += ' ' + self.str_a_case
        else:
            str_case += ' ' + scope.name

        new_scope = scope.create_child(str_case, self.str_a_case != None)
        scope.childrens_case_dict[node] = new_scope

        if self.str_a_case != None:
            scope.cases_dict[self.str_a_case] = new_scope

        count = 1
        for case in node.act_list:
            new_n_scope = new_scope.create_child('case ' + str(count) + ' ' + str_case)
            new_scope.childrens_case_dict[case] = new_n_scope
            count += 1

            self.visit(case, new_n_scope)
        
    @visitor.when(ActionNode)
    def visit(self, node, scope):
        typex = self.context.get_type(node.act_type)
        scope.define_variable(node.name, typex)

        self.visit(node.body, scope)

    def _get_type(self, ntype):
        try:
            return self.context.get_type(ntype)
        except SemanticError as e:
            self.errors.append(e.text)
            return Error_Type()    

    def scope_replet(self, scope):
        type_ = self.context.types[scope.name]

        for attr in type_.attributes:
            scope.vars_attrs_call[attr.name] = attr
        for name, method in type_.methods.items():
            scope.methods[name] = method
        scope.vars_attrs_call['self'] = type_


    def find_lets(self, scope):
        count = 1
        for child in scope.childrens:
            if len(child) > 3 and child.name[:3] == 'let': count += 1
        return 'let ' + str(count)  

    def find_blocks(self, scope):
        count = 1
        for child in scope.childrens:
            if len(child) > 5 and child.name[:5] == 'block': count += 1
        return 'block ' + str(count)  

    def find_cases(self, scope):
        count = 1
        for child in scope.childrens:
            if len(child) > 4 and child.name[:4] == 'case': count += 1
        return 'case ' + str(count)  

    def parent_scope_build(self, scope, lex_parent, type_parent):
        parent_scope = scope_find(scope, lex_parent)
        
        if parent_scope != None:
            return parent_scope
        
        parent_scope = Scope(lex_parent)
        self.scope_replet(parent_scope)
        scope.define_variable('self', type_parent)

        if parent_scope.name == 'IO':
            parent_scope.parent = scope_find(scope, 'Object')

        return parent_scope

    def scope_create(self, scope, lex):
        typex = self._get_type(lex)

        new_scope = scope.create_child(lex) if not isinstance(typex, Error_Type) else scope.create_child('Error')
        self.scope_replet(new_scope)
        new_scope.define_variable('self', typex)

        return new_scope


    def pre_order_class_walk(self, scope):
        walk = [scope]
        for child in scope.childrens:
            walk_temp = self.pre_order_class_walk(child)
            for w in walk_temp:
                walk.append(w)
        return walk

    def declaration_find(self, scp_name, declarations):
        for dec in declarations:
            if dec.id.lex == scp_name: return dec
        return None


def scope_find( scope, lex):
    if scope.name == lex:
        return scope

    for child in scope.childrens:
        scope_temp = scope_find(child, lex)
        if scope_temp != None: return scope_temp

    return None 