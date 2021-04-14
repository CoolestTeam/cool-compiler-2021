from ast_nodes import AST

class ExpressionNode(AST):
    def __init__(self):
        super(ExpressionNode, self).__init__()
        self.expr_type = None

class DynamicCallNode(ExpressionNode):
    def __init__(self, obj, method, args):
        super(DynamicCallNode, self).__init__()
        self.obj = obj
        self.method = method
        self.args = args

class StaticCallNode(ExpressionNode):
    def __init__(self, obj, static_type, method, args):
        super(StaticCallNode, self).__init__()
        self.obj = obj
        self.static_type = static_type
        self.method = method
        self.args = args

class AssignNode(ExpressionNode):
    def __init__(self, name, expression):
        super(AssignNode, self).__init__()
        self.name = name
        self.expression = expression

class IfNode(ExpressionNode):
    def __init__(self, predicate, then_expr, else_expr):
        super(IfNode, self).__init__()
        self.predicate = predicate
        self.then_expr = then_expr
        self.else_expr = else_expr

class WhileNode(ExpressionNode):
    def __init__(self, predicate, expression):
        super(WhileNode, self).__init__()
        self.predicate = predicate
        self.expression = expression

class BlockNode(ExpressionNode):
    def __init__(self, expr_list):
        super(BlockNode, self).__init__()
        self.expr_list = expr_list

class LetNode(ExpressionNode):
    def __init__(self, init_list, body):
        super(LetNode, self).__init__()
        self.init_list = init_list
        self.body = body

class CaseNode(ExpressionNode):
    def __init__(self, expression, act_list):
        super(CaseNode, self).__init__()
        self.expression = expression
        self.act_list = act_list

class NewNode(ExpressionNode):
    def __init__(self, new_type):
        super(NewNode, self).__init__()
        self.new_type = new_type

class IsVoidNode(ExpressionNode):
    def __init__(self, expression):
        super(IsVoidNode, self).__init__()
        self.expression = expression

class IdNode(ExpressionNode):
    def __init__(self, name):
        super(IdNode, self).__init__()
        self.name = name

class EqualsNode(ExpressionNode):
    def __init__(self, left, right):
        super(EqualsNode, self).__init__()
        self.left = left
        self.right = right

class IntegerNode(ExpressionNode):
    def __init__(self, value):
        super(IntegerNode, self).__init__()
        self.value = value

class StringNode(ExpressionNode):
    def __init__(self, value):
        super(StringNode, self).__init__()
        self.value = value

class BooleanNode(ExpressionNode):
    def __init__(self, value):
        super(BooleanNode, self).__init__()
        self.value = value