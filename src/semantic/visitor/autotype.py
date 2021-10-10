from semantic.tools.error import SemanticError, autotype_
from semantic.tools.type import Bool_Type, String_Type, Auto_Type, Error_Type, Int_Type
from semantic.tools.methods import MethodError
from semantic.tools.utils import get_common_basetype
from .var_collector import scope_find
from nodes import *
from .type_checker import child_scope_find
from .visitor import *

class AutoTypeVisitor(object):
    def __init__(self, context, errors=[]):
        self.context =  context
        self.errors = errors
        self.current_type = None
        self.current_method = None
        self.scope_object = None
        self.assign_autotype_check = None
        self.infer_type = None
        self.infer_meth = None


    @visitor.on('node')
    def visit(self, node, scope):
        pass

    @visitor.when(ProgramNode)
    def visit(self, node, scope):
        self.scope_object = scope
        for _ in range(5):
            for declaration in node.classes:
                self.visit(declaration, scope)
            self._get_unnassigned(scope)


    @visitor.when(ClassNode)
    def visit(self, node, scope):
        try:
            new_scope = scope.childrens_dict[node.name]
        except KeyError:
            new_scope = scope_find(scope, node.name)

        if new_scope == None: return
        
        self.current_type = self.context.get_type(node.name)

        for feat in node.features:
            if isinstance(feat, AttrInitNode) or isinstance(feat, AttrDefNode):
                self.visit(feat, new_scope)
            else:
                self.visit(feat, new_scope.childrens_dict[feat.name])
        

    @visitor.when(AttrInitNode)
    def visit(self, node, scope):

        varinfo = scope.find_variable(node.name)
        if varinfo.type.name == 'AUTO_TYPE':
            varinfo.type = self.visit(node.expression, scope)


    @visitor.when(AttrDefNode)
    def visit(self, node, scope):

        varinfo = scope.find_variable(node.name)
        if varinfo.type.name == 'AUTO_TYPE':
            if self.infer_type:
                varinfo.type = self.infer_type
            elif self.infer_meth:
                varinfo.type = self.infer_meth


    @visitor.when(ClassMethodNode)
    def visit(self, node, scope):
        self.current_method = self.current_type.get_method(node.name)

        for param, paramN, paramT in zip(node.params, self.current_method.param_names, self.current_method.param_types):
            pname = param.name
            ptype = param.param_type
            varinfo = scope.find_variable(pname)

            if varinfo.type.name != ptype:
                self.current_type.change_type(self.current_method, pname, varinfo.type)
            elif paramT.name != 'AUTO_TYPE' and varinfo.type.name == 'AUTO_TYPE':
                varinfo.type = paramT

        return_type = self.visit(node.expression, scope)

        if self.current_method.return_type.name == 'AUTO_TYPE':
            if self.infer_type:
                self.current_method.return_type = self.infer_type
            else: 
                self.current_method.return_type = return_type

        elif return_type == Auto_Type():
            self.infer_meth = self.current_method.return_type
            self.visit(node.expression, scope)
            self.infer_meth = None

    @visitor.when(LetInitNode)
    def visit(self, node, scope):

        varinfo = scope.find_variable(node.name)
        typex = self.visit(node.expression, scope)

        if varinfo.type.name == 'AUTO_TYPE':
            varinfo.type = typex

        return typex


    @visitor.when(LetDefNode)
    def visit(self, node, scope):

        varinfo = scope.find_variable(node.name)

        if varinfo.type.name == 'AUTO_TYPE':
            if self.infer_type:
                varinfo.type = self.infer_type
            if self.infer_meth:
                varinfo.type = self.infer_meth
            self.assign_autotype_check = varinfo

        return varinfo.type


    @visitor.when(AssignNode)
    def visit(self, node, scope):

        vinfo = scope.find_variable(node.name)  
        typex = self.visit(node.expression, scope)

        if vinfo.type.name == 'AUTO_TYPE':
            if self.infer_type:
                vinfo.type = self.infer_type
            if self.infer_meth:
                vinfo.type = self.infer_meth
            vinfo.type = typex 
        elif typex.name == 'AUTO_TYPE' and self.assign_autotype_check != None:
            self.assign_autotype_check.type = vinfo.type
            self.assign_autotype_check = None

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

        if stype_scope == None:
            return Auto_Type()

        cscope = scope.get_class_scope()
        ctype = self.context.get_type(cscope.name)

        meth = self._get_method(node.method, stype_scope)
        self._change_args(scope, stype, node, meth)

        if meth.return_type == Auto_Type():
            if self.infer_type:
                meth.return_type = self.infer_type
            if self.infer_meth:
                meth.return_type = self.infer_meth

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
        
        if parent_type.name == '<error>':
            parent_type_scope = self.scope_object
        else:    
            parent_type_scope = child_scope_find(self.scope_object, parent_type.name)

        if parent_type_scope == None:
            return Auto_Type()
        
        meth = self._get_method(node.method, parent_type_scope)
        self._change_args(scope, stype, node, meth)

        if meth.return_type == Auto_Type():
            if self.infer_type:
                meth.return_type = self.infer_type
            if self.infer_meth:
                meth.return_type = self.infer_meth

        return meth.return_type


    @visitor.when(ArithBinOpNode)
    def visit(self, node, scope):
        ltype, rtype = self._check_binary_node(node, scope)
        return Int_Type() if ltype == rtype == Int_Type() else Error_Type()

    @visitor.when(LogicBinOpNode)
    def visit(self, node, scope):
        ltype, rtype = self._check_binary_node(node, scope)
        return Bool_Type() if ltype == rtype == Int_Type() else Error_Type()

    @visitor.when(LogicNotNode)
    def visit(self, node, scope):
        ltype = self.visit(node.expression, scope)

        if ltype.name == 'AUTO_TYPE':
            self.assign_auto_type(ltype, node.expression, scope, Bool_Type())
            ltype = Bool_Type()
        return ltype if ltype == Bool_Type() else Error_Type()

    @visitor.when(NotNode)
    def visit(self, node, scope):
        ltype = self.visit(node.expression, scope)

        if ltype.name == 'AUTO_TYPE':
            self.assign_auto_type(ltype, node.expression, scope, Int_Type())
            ltype = Int_Type()
        return ltype if ltype == Int_Type() else Error_Type()

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
            varinfo = scope.find_variable(node.name)
            if varinfo.type.name == 'AUTO_TYPE':
                if self.infer_type:
                    varinfo.type = self.infer_type
                elif self.infer_meth:
                    varinfo.type = self.infer_meth
                self.assign_autotype_check = varinfo

            return varinfo.type
        except AttributeError:
            varinfo = scope.find_variable(node.name)
            return varinfo
    
    @visitor.when(NewNode)
    def visit(self, node, scope):
        return self.context.get_type(node.new_type)
    
    @visitor.when(IsVoidNode)
    def visit(self, node, scope):
        self.visit(node.expression, scope)
        return Bool_Type()

    @visitor.when(BlockNode)
    def visit(self, node, scope):
        infer_meth_ = self.infer_meth
        if self.infer_meth:
            self.infer_meth = None

        value = None
        exp0 = None
        for exp in node.expr_list:
            value = self.visit(exp, scope)
            exp0 = exp

        if value == Auto_Type() and infer_meth_:
            self.infer_meth = infer_meth_
            value = self.visit(exp0, scope)
            
        return value

    @visitor.when(LetNode)
    def visit(self, node, scope):
        try:
        	new_scope = scope.childrens_let_dict[node]
        except KeyError:
        	new_scope = scope

            
        infer_meth_ = self.infer_meth
        
        if self.infer_meth:
            self.infer_meth = None
        
        for init in node.init_list:
            self.visit(init, new_scope)
        
        if infer_meth_:
            self.infer_meth = infer_meth_

        return self.visit(node.body, new_scope)
    
    @visitor.when(WhileNode)
    def visit(self, node, scope):
        infer_meth_ = self.infer_meth

        if self.infer_meth:
            self.infer_meth = None

        typex = self.visit(node.predicate, scope)
        
        if typex == Auto_Type():
            self.assign_auto_type(typex, node.predicate, scope, Bool_Type())
        
        if infer_meth_:
            self.infer_meth = infer_meth_

        self.visit(node.expression, scope)
        return self.context.get_type('Object')


    @visitor.when(IfNode)
    def visit(self, node, scope):
        infer_meth_ = self.infer_meth

        if self.infer_meth:
            self.infer_meth = None

        self.visit(node.predicate, scope)

        true_type = self.visit(node.then_expr, scope)
        false_type = self.visit(node.else_expr, scope)

        if true_type.name == 'AUTO_TYPE' and false_type.name != 'AUTO_TYPE':
            self.assign_auto_type(true_type, node.then_expr, scope, false_type)
            true_type = false_type
        elif false_type.name == 'AUTO_TYPE' and true_type.name != 'AUTO_TYPE':
            self.assign_auto_type(false_type, node.else_expr, scope, true_type)
            false_type = true_type

        if infer_meth_:
            self.infer_meth = infer_meth_

        return get_common_basetype([true_type, false_type])


    @visitor.when(CaseNode) 
    def visit(self, node, scope):
        infer_meth_ = self.infer_meth
        
        if self.infer_meth:
            self.infer_meth = None

        type_expr = self.visit(node.expression, scope)
        new_scope = scope.childrens_case_dict[node]

        types = []
        
        for case in node.act_list:
            new_n_scope = new_scope.childrens_case_dict[case]
            types.append(self.visit(case, new_n_scope))

        if infer_meth_:
            self.infer_meth = infer_meth_
        
        return get_common_basetype(types)

    @visitor.when(ActionNode)
    def visit(self, node, scope):
        var_info = scope.find_variable(node.name)
        typex = self.visit(node.body, scope)

        if var_info.type.name == 'AUTO_TYPE':
            if typex == Auto_Type() and self.infer_meth:
                typex = self.infer_meth

            var_info.type = typex

        return typex


    def assign_auto_type(self, typex, node, scope, other_type):
        if isinstance(node, Variable_Node):
            varinfo = scope.find_variable(node.name)
            varinfo.type = other_type
        elif isinstance(node, (DynamicCallNode, StaticCallNode)):
            if isinstance(node, DynamicCallNode):
                typex = self.visit(node.obj, scope)
            elif isinstance(node, StaticCallNode):
                typex = self.current_type
            meth = typex.get_method(node.method)
            meth.return_type = other_type

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
    
    def _get_unnassigned(self, scope):
        for name, typex in scope.vars_attrs_call.items():
            if name == 'self': continue
            if typex.name == 'AUTO_TYPE':
                self.errors.append(autotype_ % name)

        for child in scope.childrens:
            self._get_unnassigned(child)

    def _change_args(self, scope, stype, node, meth):
        args = [arg for arg in node.args]
        arg_types = [self.visit(arg, scope) for arg in node.args]
        scp = child_scope_find(self.scope_object, stype.name)
        
        for arg, atype, ptype, pname in zip(args, arg_types, meth.param_types, meth.param_names):
            if ptype == Auto_Type() and atype != Auto_Type():
                varinfo = scp.find_variable(pname)
                varinfo.type = atype
                stype.change_type(meth, pname, varinfo.type)

            if ptype != Auto_Type() and atype == Auto_Type():
                self.infer_type = ptype
                self.visit(arg, scope)
                self.infer_type = None


    def _check_binary_node(self, node, scope):
        ltype = self.visit(node.left, scope)
        if ltype.name == 'AUTO_TYPE':
            self.assign_auto_type(ltype, node.left, scope, Int_Type())
            ltype = Int_Type()

        rtype = self.visit(node.right, scope)
        if rtype.name == 'AUTO_TYPE':
            self.assign_auto_type(rtype, node.right, scope, Int_Type())
            rtype = Int_Type()
        return ltype, rtype

    def _get_type(self, ntype):
        try:
            return self.context.get_type(ntype)
        except SemanticError as e:
            self.errors.append(e.text)
            return Error_Type()