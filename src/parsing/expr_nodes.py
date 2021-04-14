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