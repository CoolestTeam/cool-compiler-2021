from semantic.tools.error import incompatible_types_, wrong_signature_, incorrect_type_, too_many_args_, missing_params_, b_op_not_defined_, u_op_not_defined_, SemanticError
from semantic.tools.type import Error_Type, Bool_Type, String_Type, Int_Type, Auto_Type
from semantic.tools.methods import MethodError
from nodes import *
from .visitor import *
from semantic.tools.utils import get_common_basetype
from .var_collector import scope_find


class TypeChecker:
    def __init__(self, context, errors=[]):
        self.context = context
        self.current_type = None
        self.current_method = None
        self.errors = errors
        self.scope_object = None
        self.call_atr = None
        self.call_var = None
        

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

        for feat in node.features:
            if isinstance(feat, Attr_Args_Node):
                self.visit(feat, new_scope)
            else:
                self.visit(feat, new_scope.childrens_dict[feat.id])

    @visitor.when(AttrInitNode)
    def visit(self, node, scope):
        varinfo = scope.find_variable(node.name)
        
        self.call_atr = node.name
        typex = self.visit(node.expression, scope)
        self.call_atr = None
        if not typex.conforms_to(varinfo.type):
            self.errors.append(incompatible_types_ %(typex.name, varinfo.type.name))
            return Error_Type()

        varinfo.type = typex
        return typex

    @visitor.when(AttrDefNode)
    def visit(self, node, scope):
        return self._get_type(node.attr_type)

    @visitor.when(ClassMethodNode)
    def visit(self, node, scope):
        parent = self.current_type.parent 
        pnames = [param.name for param in node.params]
        ptypes = [param.param_type for param in node.params]

        for i in range(len(pnames)):
            if pnames[i] == 'self':
                self.errors.append(incompatible_types_ % (pnames[i], ptypes[i]))

        self.current_method = method = self.current_type.get_method(node.name)
        if parent is not None:
            try:
                old_meth = parent.get_method(node.name)
                if old_meth.return_type.name != method.return_type.name:
                    if node.return_type != 'SELF_TYPE':
                        self.errors.append(wrong_signature_ % (node.name, parent.name))
                
                else:
                    for name, type1, type2 in zip(ptypes, method.param_types, old_meth.param_types):
                        if type1.name != type2.name:
                            if name != 'SELF_TYPE':
                                self.errors.append(wrong_signature_ % (node.name, parent.name))
            except SemanticError:
                pass

        result = self.visit(node.expression, scope)
        if not result.conforms_to(method.return_type):
            self.errors.append(incompatible_types_ %(method.return_type.name, result.name))

    @visitor.when(LetInitNode)
    def visit(self, node, scope):

        var_info = scope.find_variable(node.name)
        vtype = var_info.type

        self.call_var = node.name
        typex = self.visit(node.expression, scope)
        self.call_var = None
        if not typex.conforms_to(var_info.type):
            self.errors.append(incompatible_types_ %(vtype.name, typex.name))

        return typex

    @visitor.when(LetDefNode)
    def visit(self, node, scope):

        var_info = scope.find_variable(node.name)
        vtype = var_info.type

        return vtype
        
    @visitor.when(AssignNode)
    def visit(self, node, scope):
        vinfo = scope.find_variable(node.name)
        vtype = vinfo.type
            
        typex = self.visit(node.expression, scope)

        if not typex.conforms_to(vtype):
            self.errors.append(incompatible_types_ %(vtype.name, typex.name))
        return typex

    @visitor.when(DynamicCallNode)
    def visit(self, node, scope):
        try:
            stype = scope.find_variable(node.obj.name).type
        except AttributeError:
            #cuando es funcion
            stype = self.visit(node.obj, scope)

        if stype.name == '<error>':
            stype = self.visit(node.obj, scope)

        if stype.name == '<error>':
            stype_scope = self.scope_object
        else: stype_scope = child_scope_find(self.scope_object, stype.name)

        meth = self._get_method(node.method, stype_scope)
        self._check_args(meth, scope, node.args)

        if meth.return_type.name != 'SELF_TYPE':
            self.define_call(str(node), meth.return_type, scope)
        else:
            self.define_call(str(node), stype, scope)
        
        return meth.return_type

    @visitor.when(StaticCallNode)
    def visit(self, node, scope):
        try:
            stype = scope.find_variable(node.obj.name).type
        except AttributeError:
            #cuando es funcion
            stype = self.visit(node.obj, scope)

        parent_type = self._get_type(node.static_type)

        if stype.name == '<error>':
            stype = self.visit(node.obj, scope)

        if not parent_type.conforms_to(stype):
            self.errors.append(incompatible_types_ % (typex.name, obj.name))
            return Error_Type()
        
        if parent_type.name == '<error>':
            parent_type_scope = self.scope_object
        else:    
            parent_type_scope = child_scope_find(self.scope_object, parent_type.name)
        
        meth = self._get_method(node.method, parent_type_scope)
        self._check_args(meth, scope, node.args)
        
        if meth.return_type.name != 'SELF_TYPE':
            self.define_call(str(node), meth.return_type, scope)
        else:
            self.define_call(str(node), stype, scope)

        return meth.return_type


    @visitor.when(IntegerNode)
    def visit(self, node, scope):
        return Int_Type()

    @visitor.when(BooleanNode)
    def visit(self, node, scope):
        return Bool_Type()

    @visitor.when(StringNode)
    def visit(self, node, scope):
        return String_Type()

    @visitor.when(IdNode)
    def visit(self, node, scope):
        try:
            return scope.find_variable(node.name).type
        except AttributeError:
            return scope.find_variable(node.name)

    @visitor.when(NewNode)
    def visit(self, node, scope):
        return self._get_type(node.name)

    @visitor.when(WhileNode)
    def visit(self, node, scope):
        cond = self.visit(node.predicate, scope)
        
        if cond.name != 'Bool':
            self.errors.append(incorrect_type_ % (cond.name, 'Bool'))   
        return self.visit(node.expression, scope)

    @visitor.when(IsVoidNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope)
        return Bool_Type()

    @visitor.when(IfNode)
    def visit(self, node, scope):
        cond = self.visit(node.predicate, scope)

        if cond.name != 'Bool':
            self.errors.append(incorrect_type_ % (cond.name, 'Bool'))
        
        true_type = self.visit(node.then_expr, scope)
        false_type = self.visit(node.else_expr, scope)
      
        if true_type.conforms_to(false_type):
            return false_type
        elif false_type.conforms_to(true_type):
            return true_type
        else:
            self.errors.append(incompatible_types_ % (false_type.name, true_type.name))
            return Error_Type()

    @visitor.when(BlockNode)
    def visit(self, node, scope):
        value = None
        for exp in node.expr_list:
            value = self.visit(exp, scope)
        return value

    @visitor.when(LetNode)
    def visit(self, node, scope):
        try:
            new_scope = scope.childrens_let_dict[node]
        except KeyError:
            new_scope = scope

        for init in node.init_list:
            self.visit(init, new_scope)
        return self.visit(node.expression, new_scope)
    
    @visitor.when(CaseNode) 
    def visit(self, node, scope):

        type_expr = self.visit(node.expression, scope)

        new_scope = scope.childrens_case_dict[node]

        types = []
        var_types = []
        for case in node.act_list:
            new_n_scope = new_scope.childrens_case_dict[case]
            t, vt = self.visit(case, new_n_scope)

            types.append(self._get_type(t.name))
            var_types.append(self._get_type(vt.type.name))

            if not t.conforms_to(vt.type):
                self.errors.append(incompatible_types_ % (t.name, vt.type.name))
                return Error_Type()
            else:
                vt.type = t

        for t in var_types:
            if not type_expr.conforms_to(t):
                self.errors.append(incompatible_types_ % (t.name, type_expr.name))
                return Error_Type()

        return get_common_basetype(types)

    @visitor.when(ActionNode)
    def visit(self, node, scope):
        var_info = scope.find_variable(node.name)
        typex = self.visit(node.body, scope)
        return typex, var_info
            
    @visitor.when(ArithBinOpNode)
    def visit(self, node, scope):
        ltype = self.visit(node.left, scope)
        rtype = self.visit(node.right, scope)
        if ltype != rtype != Int_Type():
            self.errors.append(b_op_not_defined_ %('Arithmetic', ltype.name, rtype.name))
            return Error_Type()
        return Int_Type()

    @visitor.when(LogicBinOpNode)
    def visit(self, node, scope):
        ltype = self.visit(node.left, scope)
        rtype = self.visit(node.right, scope)
        if ltype != rtype != Int_Type():
            self.errors.append(b_op_not_defined_ %('Logical', ltype.name, rtype.name))
            return Error_Type()

        return Bool_Type()

    @visitor.when(LogicNotNode)
    def visit(self, node, scope):
        ltype = self.visit(node.expression, scope)
        if ltype != Bool_Type():
            self.errors.append(u_op_not_defined_ %('Logical', ltype.name))
            return Error_Type()

        return Bool_Type()

    @visitor.when(NotNode)
    def visit(self, node, scope):
        ltype = self.visit(node.expression, scope)
        if ltype != Int_Type():
            self.errors.append(u_op_not_defined_ %('Arithmetic', ltype.name))
            return Error_Type()
        return Int_Type()


    def _get_type(self, ntype):
        try:
            return self.context.get_type(ntype)
        except SemanticError as e:
            self.errors.append(e.text)
            return Error_Type()

    def _get_method(self, name, scope):
        try:
            typex = self._get_type(scope.name)
            return typex.get_method(name)
        except SemanticError as e:
            if typex != Error_Type() and typex != Auto_Type():
                if scope.name == 'Object':
                    self.errors.append(e.text)
                else:
                    return self._get_method(name, scope.parent.get_class_scope())
            return MethodError(name, [], [], Error_Type())


    def _check_args(self, meth, scope, args):
        arg_types = [self.visit(arg, scope) for arg in args]
        
        if len(arg_types) > len(meth.param_types):
            self.errors.append(too_many_args_ % meth.name)
        elif len(arg_types) < len(meth.param_types):
            for arg in meth.param_names[len(arg_types):]:
                self.errors.append(missing_params_ % (arg, meth.name))

        for atype, ptype in zip(arg_types, meth.param_types):
            if not atype.conforms_to(ptype):
                self.errors.append(incompatible_types_ % (ptype.name, atype.name))

    def define_call(self, node_id, return_type, scope):
        var_atr = None
        if self.call_atr != None: 
            var_atr = self.call_atr
        elif self.call_var != None:
            var_atr = self.call_var
        else:
            var_atr = scope.name 

        scope.define_call(node_id, return_type, var_atr)


def child_scope_find(scope, name):
        try:
            return scope.childrens_dict[name]
        except KeyError:
            for child in scope.childrens:
                solve = child_scope_find(child, name)
                if not solve is None: 
                    return solve
            return None
