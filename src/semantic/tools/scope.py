import itertools as itt
from .var import VariableInfo
from .type import Error_Type

class Scope:
    def __init__(self, name, parent=None):
        self.name = name
        self.vars_attrs_call = {}
        self.methods = {}
        self.parent = parent
        self.childrens = []
        self.childrens_dict = {}
        self.childrens_let_dict = {}
        self.childrens_case_dict = {}
        self.is_class = False 
        self.cases_dict = {}
        self.func_dict = {}
        self.call_dict = {}

    def __len__(self):
        return len(self.vars_attrs_call) + len(self.methods) + len(self.childrens)

    def __str__(self):

        ans = self.name + ': \n'
        res = '\n' + ans
        if len(self.vars_attrs_call) > 0:
            for key, value in self.vars_attrs_call.items():
                if key == 'self':
                    res += ('\t' + ('\n' + '\t')) + '[attribute] self : ' + str(self.name) + ',\n'
                else:
                    res += ('\t' + ('\n' + '\t')) + '[attribute or variable]' + str(value) + ',\n'

        if len(self.methods) > 0:
            res += ('\t' + ('\n' + '\t')) + ','.join(y for x in self.methods.values() for y in str(x).split('\n \n')) + ',\n'

        for scope in self.childrens:
            res += self.tab_level(1, scope)
        return res

    def tab_level(self, tabs, scope):
        ans = scope.name + ': \n'

        res = ('\t' * tabs) +  ('\n' + ('\t' * tabs)) + ans
        if len(scope.vars_attrs_call) > 0:

            for key, value in scope.vars_attrs_call.items():
                if key == 'self':
                    res += ('\t' * tabs) +  ('\n' + ('\t' * tabs)) + '[attribute] self : ' + str(scope.name) + ',\n'
                else:
                    try:
                        if value.__contains__('(') and not scope.is_class:
                            res += ('\t' * tabs) +  ('\n' + ('\t' * tabs)) + '[call]: ' + str(value) + ',\n'
                    except AttributeError:
                        res += ('\t' * tabs) +  ('\n' + ('\t' * tabs)) + '[attribute or variable]' + str(value) + ',\n'

                        try:
                            res += self.tab_level(tabs + 1, scope.cases_dict[key])
                        except KeyError:
                            pass

                        try:
                            for y in scope.call_dict[key]:
                                res += ('\t' * (tabs + 1)) +  ('\n' + ('\t' * (tabs + 1))) + '[call]: '+ y + ', \n'
                        except KeyError:
                            pass

        if len(scope.methods) > 0:
            for key, value in scope.methods.items():
                res += ('\t' * tabs) +  ('\n' + ('\t' * tabs)) + str(value) + ',\n'

                try:
                    res += self.tab_level(tabs + 1, scope.func_dict[key])
                except KeyError:
                    pass

        for child in scope.childrens:
            if child.name in scope.func_dict.keys(): 
                continue

            res += self.tab_level(tabs + 1, child)
        
        return res

    def __repr__(self):
        return str(self)

    def create_child(self, name, is_case_attribute = False):
        child = Scope(name, self)
        if not is_case_attribute:
            self.childrens.append(child)
            self.childrens_dict[name] = child
        return child

    def define_variable(self, vname, vtype):
        info = VariableInfo(vname, vtype)
        self.vars_attrs_call[vname] = info
        return info

    def define_call(self, call_, ctype, var_atr):
        self.vars_attrs_call[call_] = call_ + ':' + ctype.name
        try:
            self.call_dict[var_atr].append(self.vars_attrs_call[call_])
        except KeyError:
            self.call_dict[var_atr] = [self.vars_attrs_call[call_], ]

    def find_variable(self, vname):
        try:
            return self.vars_attrs_call[vname]
        except KeyError:
            if self.parent == None: return VariableInfo(vname, Error_Type())
            return self.parent.find_variable(vname)
        
    def get_class_scope(self):
        if self.is_class: return self
        return self.parent.get_class_scope()

    def is_defined(self, vname):

        try:
            var = self.vars_attrs_call[vname]
            return True
        except KeyError:
            if self.parent == None: return False
            return self.parent.is_defined(vname)

    def is_defined_local(self, vname):
        return vname in self.vars_attrs_call
        
    def is_local(self, vname):
        return vname in self.vars_attrs_call

    def define_attribute(self, attr):
        self.vars_attrs_call[attr.name] = attr

    def children_scope_class_delete(self, name):
        for child in self.childrens:
            if child.name == name:
                self.childrens.remove(child)
                break
        self.childrens_dict.pop(name)

    def add_child(self, scope_child):
        scope_child.chains_parent(self)
        self.childrens.append(scope_child)
        self.childrens_dict[scope_child.name] = scope_child

    def chains_parent(self, new_parent):
        self.parent = new_parent