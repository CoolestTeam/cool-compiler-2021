from .visitor.type_collector import TypeCollector
from .visitor.type_builder import TypeBuilder
from .visitor.var_collector import VarCollector
from .visitor.selftype import SelfTypeVisitor
from .visitor.autotype import AutoTypeVisitor
from .visitor.type_checker import TypeChecker


class MySemanticAnalyzer:
	def __init__(self, ast):
		self.ast = ast
		self.errors = []

		self.type_collector =  None
		self.type_builder = None
		self.var_collector = None
		self.self_type = None
		self.auto_type = None
		self.type_checker = None

	def analyze(self):

		self.type_collector = TypeCollector(self.errors)
		self.type_collector.visit(self.ast)
		context = self.type_collector.context

		if len(self.errors) > 0:
			return context, None, self.errors

		#building types
		self.type_builder = TypeBuilder(context, self.errors)
		self.type_builder.visit(self.ast)

		if len(self.errors) > 0: 
			return context, None, self.errors
	
		#var collector
		self.var_collector = VarCollector(context, self.errors)
		scope = self.var_collector.visit(self.ast)

		if len(self.errors) > 0: 
			return context, scope, self.errors

		#self type
		self.self_type = SelfTypeVisitor(context, self.errors)
		self.self_type.visit(self.ast, scope)

		if len(self.errors) > 0: 
			return context, scope, self.errors
	
		#auto type
		self.auto_type = AutoTypeVisitor(context, self.errors)
		self.auto_type.visit(self.ast, scope)

		#self type
		self.self_type = SelfTypeVisitor(context, self.errors)
		self.self_type.visit(self.ast, scope)

	
		if len(self.errors) > 0: 
			return context, scope, self.errors

		#checking types
		self.type_checker = TypeChecker(context, self.errors)
		self.type_checker.visit(self.ast, scope)

		return context, scope