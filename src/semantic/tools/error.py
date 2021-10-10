import itertools as itt

#semantic errors
wrong_signature_ = 'Method "%s" already defined in "%s" with a different signature.'
read_only_ = 'Variable "self" is read-only.'
local_already_defined_ = 'Variable "%s" is already defined in method "%s".'
incompatible_types_ = 'Cannot convert "%s" into "%s".'
var_not_defined_ = 'Variable "%s" is not defined in "%s".'
invalid_op_ = 'Operation is not defined between "%s" and "%s".'
incorrect_type_ = 'Incorrect type "%s" waiting "%s"'
autotype_ = 'Cannot infer the type of "%s"'
used_before_assignment_ = 'Variable "%s" used before being assigned'
circular_dependency_ = 'Circular dependency between %s and %s'
b_op_not_defined_ = '%s operations are not defined between "%s" and "%s"'
u_op_not_defined_ = '%s operations are not defined for "%s"'
missing_params_ = 'Missing argument "%s" in function call "%s"'
too_many_args_ = 'Too many arguments for function call "%s"'


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]