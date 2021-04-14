from expr_nodes import ExpressionNode

class ArithBinOpNode(ExpressionNode):
    def __init__(self):
        super(ArithBinOpNode, self).__init__()
        pass

class LogicBinOpNode(ExpressionNode):
    def __init__(self):
        super(LogicBinOpNode, self).__init__()
        pass

class NotNode(ExpressionNode):
    def __init__(self, expression):
        super(NotNode, self).__init__()
        self.expression = expression