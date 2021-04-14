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

class LogicNotNode(ExpressionNode):
    def __init__(self, expression):
        super(LogicNotNode, self).__init__()
        self.expression = expression

class SumNode(ArithBinOpNode):
    def __init__(self, left, right):
        super(SumNode, self).__init__()
        self.left = left
        self.right = right

class SubNode(ArithBinOpNode):
    def __init__(self, left, right):
        super(SubNode, self).__init__()
        self.left = left
        self.right = right

class MultNode(ArithBinOpNode):
    def __init__(self, left, right):
        super(MultNode, self).__init__()
        self.left = left
        self.right = right

class DivNode(ArithBinOpNode):
    def __init__(self, left, right):
        super(DivNode, self).__init__()
        self.left = left
        self.right = right

class LessNode(LogicBinOpNode):
    def __init__(self, left, right):
        super(LessThanNode, self).__init__()
        self.left = left
        self.right = right

class LessEqualNode(LogicBinOpNode):
    def __init__(self, left, right):
        super(LessOrEqualThanNode, self).__init__()
        self.left = left
        self.right = right