import ply.yacc as yacc
from nodes import *
from lexer import MyLexer
from syntactic_error import SyntaxError
import sys

class MyParser():
    def __init__(self):
        self.build()

    # Build the parser
    def build(self, **kwargs):
        self.lexer = MyLexer()
        self.tokens = self.lexer.tokens
        self.errors = []
        self.parser = yacc.yacc(module=self)

    def parse(self, _cool_program):
        return self.parser.parse(_cool_program)
    
    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT')
        ('nonassoc', 'LESS', 'LESSEQ', 'EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'NOX'),
        ('right', 'ARROBA'),
        ('right', 'DOT')
    )

    # Grammar rules functions
    def p_program(self, p):
        p[0] = ProgramNode(classes=p[1])
    
    def p_class_list(self, p):
        p[0] = (p[1],) if len(p) == 3 else p[1] + (p[2],)

    def p_def_class(self, p):
        p[0] = ClassNode(
            name=p[2], parent='Object', features=p[4], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))

    def p_def_class_inherits(self, p):
        p[0] = ClassNode(
            name=p[2], parent=p[4], features=p[6], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(4)))

    def p_feature_list(self, p):
        p[0] = (p[1],) if len(p) == 3 else p[1] + (p[2],)
    
    def p_feature_opt(self, p):
        p[0] = tuple() if p.slice[1].type == 'empty' else p[1]
    
    def p_features_f_class_method(self, p):
        p[0] = ClassMethodNode(
            name=p[1], params=p[3], expression=p[8], return_type=p[6], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_features_class_method(self, p):
        p[0] = ClassMethodNode(
            name=p[1], params=tuple(), expression=p[7], return_type=p[5], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_features_attr(self, p):
        p[0] = p[1]

    def p_attr_init(self, p):
        p[0] = p[1] if len(p) == 2 else AttrInitNode(
            name=p[1], attr_type=p[3], expression=p[5], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))
        
    def p_attr_def(self, p):
        p[0] = AttrDefNode(
            name=p[1], attr_type=p[3], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_action_list(self, p):
        p[0] = (p[1],) if len(p) == 2 else tuple(p[1]) + (p[2],)

    def p_action(self, p):
        p[0] = ActionNode(
            name=p[1], act_type=p[3], body=p[5], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_let_var(self, p):
        p[0] = (p[1],) if len(p) == 2 else p[1] + (p[3],)
    
    def p_let_init(self, p):
        p[0] = (p[1],) if len(p) == 2 else LetInitNode(
            name=p[1], let_type=p[3], expression=p[5], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))            

    def p_let_def(self, p):
        p[0] = p[1] if len(p) == 2 else LetDefNode(
            name=p[1], let_type=p[3], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_formal_param_list(self, p):
        p[0] = (p[1],) if len(p) == 2 else p[1] + (p[3],)
    
    def p_formal_param(self, p):
        p[0] = FormalParamNode(
            name=p[1], param_type=p[3], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))
    
    def p_args_list(self, p):
        p[0] = (p[1],) if len(p) == 2 else p[1] + (p[3],)
    
    def p_args_list_opt(self, p):
        p[0] = tuple() if p.slice[1].type == 'empty' else p[1]
    
    def p_expr_dynamic_call(self, p):
        p[0] = DynamicCallNode(
            obj=p[1], method=p[3], args=p[5], row=p.lineno(3), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(3)))
    
    def p_expr_static_call(self, p):
        p[0] = StaticCallNode(
            obj=p[1], static_type=p[3], method=p[5], args=p[7], row=p.lineno(5), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(5)))

    def p_expr_self_call(self, p):
        p[0] = DynamicCallNode(
            obj=IdNode('self', row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1))), method=p[1], args=p[3], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))
    
    def p_expr_assign(self, p):
        p[0] = AssignNode(
            name=p[1], expression=p[3], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_if(self, p):
        p[0] = IfNode(
            predicate=p[2], then_expr=p[4], else_expr=p[6], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_while(self, p):
        p[0] = WhileNode(
            predicate=p[2], expression=p[4], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_block_list(self, p):
        p[0] = (p[1],) if len(p) == 3 else p[1] + (p[2],)
    
    def p_expr_block(self, p):
        p[0] = BlockNode(
            expr_list=p[2], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_let(self, p):
        p[0] = LetNode(
            init_list=p[2], body=p[4], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))

    def p_expr_case(self, p):
        p[0] = CaseNode(
            expression=p[2], act_list=p[4], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_new(self, p):
        p[0] = NewNode(
            new_type=p[2], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))

    def p_expr_isvoid(self, p):
        p[0] = IsVoidNode(
            expression=p[2], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))

    def p_expr_id(self, p):
        p[0] = IdNode(
            name=p[1], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_int(self, p):
        p[0] = IntegerNode(
            value=p[1], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_str(self, p):
        p[0] = StringNode(
            value=p[1], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_bool(self, p):
        p[0] = BooleanNode(
            value=p[1], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))
    
    def p_expr_binary_op(self, p):
        if p[2] == '+':
            p[0] = SumNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '-':
            p[0] = SubNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '*':
            p[0] = MultNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '/':
            p[0] = DivNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '<':
            p[0] = LessNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '<=':
            p[0] = LessEqualNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
        elif p[2] == '=':
            p[0] = EqualsNode(
                left=p[1], right=p[3], row=p.lineno(2), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(2)))
    
    def p_expr_unary_op(self, p):
        if p[1] == '~':
            p[0] = LogicNotNode(
                expression=p[2], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))
        elif p[1].lower() == 'not':
            p[0] = NotNode(
                expression=p[2], row=p.lineno(1), col=MyLexer.find_col(p.lexer.lexdata, p.lexpos(1)))

    def p_expr_parenthesis(self, p):
        p[0] = p[2]

    def p_empty(self, p):
        p[0] = None
    
    def p_error(self, p):
        if p:
            self.errors.append(SyntaxError(f'"ERROR at or near {p.value}"', p.lineno, MyLexer.find_col(p.lexer.lexdata, p.lexpos))
            self.parser.errok()
        else:
            self.errors.append(SyntaxError('"ERROR at or near EOF"',0,0))
            return
        

if __name__ == "__main__":
    _file = sys.argv[1]
    _cool_program = open(_file, encoding="utf-8").read()

    _myparser = MyParser()
    _myparse_result = _myparser.parse(_cool_program)

    if _myparser.errors:
        print(_myparser.errors[0])