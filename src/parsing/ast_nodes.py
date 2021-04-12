class AST:
    def __init__(self):
        pass

class ProgramNode(AST):
    def __init__(self, classes):
        super(ProgramNode, self).__init__()
        self.classes = classes

class ClassNode(AST):
    def __init__(self, name, parent, features):
        super(ClassNode, self).__init__()
        self.name = name
        self.parent = parent
        self.features = features

class ClassMethodNode(AST):
    def __init__(self, name, params, expression, return_type):
        super(ClassMethodNode, self).__init__()
        self.name = name
        self.params = params
        self.expression = expression
        self.return_type = return_type

class AttrInitNode(AST):
    def __init__(self, name, attr_type, expression):
        super(AttrInitNode, self).__init__()
        self.name = name
        self.attr_type = attr_type
        self.expression = expression

class AttrDefNode(AST):
    def __init__(self, name, attr_type):
        super(AttrDefNode, self).__init__()
        self.name = name
        self.attr_type = attr_type

class ActionNode(AST):
    def __init__(self, name, act_type, body):
        super(ActionNode, self).__init__()
        self.name = name
        self.act_type = act_type
        self.body = body

class LetInitNode(AST):
    def __init__(self, name, let_type, expression):
        super(LetInitNode, self).__init__()
        self.name = name
        self.let_type = let_type
        self.expression = expression