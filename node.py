# Graham Smith gsmith98@jhu.edu

from customexception import CustException
from entry import *


class Node(object):
    def accept(self, visitor):
        return visitor.node_visit(self)

    def to_string(self):
        return "Node"


class Instruction(Node):
    def __init__(self):
        self.__next_instr = None

    def give_next(self, instr):
        self.__next_instr = instr

    def get_next(self):
        return self.__next_instr

    def has_next(self):
        if self.__next_instr is None:
            return False
        else:
            return True

    def to_string(self):
        return "Instruction"


class Expression(Node):
    def __init__(self, typ):
        self.__type = typ

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def to_string(self):
        return "Expression of type " + self.__type.to_string()


class ProcedureCall(Instruction):
    def __init__(self, proc_ent, actuals):
        self.__proc = proc_ent
        self.__actuals = actuals
        Instruction.__init__(self)

    def get_proc(self):
        return self.__proc

    def get_actuals(self):
        return self.__actuals


class FunctionCall(Expression):
    def __init__(self, proc_ent, actuals):
        self.__proc = proc_ent
        self.__actuals = actuals

    def get_proc(self):
        return self.__proc

    def get_actuals(self):
        return self.__actuals

    def get_type(self):
        return self.__proc.get_type()

class Condition(Node):
    def __init__(self, relate, left, right):
        self.__relation = relate  # string relation
        self.__left_exp = left
        self.__right_exp = right

    def get_rel(self):
        return self.__relation

    def get_left(self):
        return self.__left_exp

    def get_right(self):
        return self.__right_exp

    def negate(self):
        if self.__relation == "=":
            opp = "#"
        elif self.__relation == "#":
            opp = "="
        elif self.__relation == "<":
            opp = ">="
        elif self.__relation == ">=":
            opp = "<"
        elif self.__relation == ">":
            opp = "<="
        elif self.__relation == "<=":
            opp = ">"

        return Condition(opp, self.__left_exp, self.__right_exp)

    def to_string(self):
        return "Condition " + self.__relation


class Assign(Instruction):
    def __init__(self, loc, express):
        self.__location = loc
        self.__exp = express
        Instruction.__init__(self)

    def get_loc(self):
        return self.__location

    def get_exp(self):
        return self.__exp

    def to_string(self):
        return "Assign to a(n) " + self.__location.get_type().to_string()


class If(Instruction):
    def __init__(self, cond, tru, fals=None):
        self.__condition = cond
        self.__instrs_true = tru
        self.__instrs_false = fals
        Instruction.__init__(self)

    def get_cond(self):
        return self.__condition

    def get_true(self):
        return self.__instrs_true

    def get_false(self):
        return self.__instrs_false

    def has_false(self):
        return (self.__instrs_false is not None)

    def to_string(self):
        return "If statement"


class Repeat(Instruction):
    def __init__(self, cond, instructions):
        self.__condition = cond
        self.__instrs = instructions
        Instruction.__init__(self)

    def get_cond(self):
        return self.__condition

    def get_instrs(self):
        return self.__instrs

    def to_string(self):
        return "Repeat statement"


class Read(Instruction):
    def __init__(self, loc):
        self.__location = loc
        Instruction.__init__(self)

    def get_loc(self):
        return self.__location

    def to_string(self):
        return "Read into an integer variable"


class Write(Instruction):
    def __init__(self, express):
        self.__exp = express
        Instruction.__init__(self)

    def get_exp(self):
        return self.__exp

    def to_string(self):
        return "Write statement"


# literal numbers and identifiers referring
# to Constant entries will both use Number
class Number(Expression):
    def __init__(self, const):
        self.__constant = const  # Entry
        self.__type = const.getType()

    def get_const(self):
        return self.__constant

    def get_value(self):
        return self.__constant.getValue()

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def to_string(self):
        return "Number " + str(self.get_value())


class Location(Expression):
    pass


class Binary(Expression):
    def __new__(cls, op, left, right):
        if not (isinstance(left.get_type(), Integer)
            and isinstance(right.get_type(), Integer)):
            raise CustException("Arithmetic operator used on non-integer(s)")

        # Constant folding =====================================
        if isinstance(left, Number) and isinstance(right, Number):
            num1 = left.get_value()
            num2 = right.get_value()

            if op == "+":
                num3 = num1 + num2
            elif op == "-":
                num3 = num1 - num2
            elif op == "*":
                num3 = num1 * num2
            elif op == "DIV":
                if num2 == 0:
                    raise CustException("Explicit DIV by 0")
                num3 = num1 / num2
            elif op == "MOD":
                if num2 == 0:
                    raise CustException("Explicit MOD by 0")
                num3 = num1 % num2
            return Number(Constant(Integer(), num3))
        else:
            return Expression.__new__(cls)

    def __init__(self, op, left, right):
        self.__operator = op
        self.__exp_left = left
        self.__exp_right = right
        self.__type = Integer()

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def get_op(self):
        return self.__operator

    def get_left(self):
        return self.__exp_left

    def get_right(self):
        return self.__exp_right

    def to_string(self):
        return "Binary " + self.__operator


# Named differently to avoid confusion with the entry
class Var(Location):
    def __new__(cls, var, nomen):
        if isinstance(var, Constant):
            return Number(var)
        else:
            return Expression.__new__(cls)

    def __init__(self, var, nomen):
        self.__variable = var  # Entry
        self.__type = var.getType()  # Type Entry
        self.__name = nomen

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def get_var(self):
        return self.__variable

    def get_name(self):
        return self.__name

    def to_string(self):
        return ("Variable " + self.__name + " of type "
            + self.get_type.to_string())


class Index(Location):
    def __init__(self, loc, express):
        self.__location = loc
        self.__exp = express
        # later will have to check that index value is in bounds

        if not isinstance(self.__location.get_type(), Array):
            raise CustException("Non-Arrays can't be indexed")

        if not isinstance(self.__exp.get_type(), Integer):
            raise CustException("Indeces must be of type Integer")

        # loc is a node holding an array for its type entry
        self.__type = loc.get_type().getType()  # elemtype

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def get_loc(self):
        return self.__location

    def get_exp(self):
        return self.__exp

    def to_string(self):
        return "Index"


class Field(Location):
    def __init__(self, loc, varName):
        self.__location = loc

        if not isinstance(loc.get_type(), Record):
            raise CustException("No fields for Non-Records")

        var_entry = loc.get_type().getScope().find(varName)

        if var_entry is None:
            raise CustException("Record has no field " + varName)

        self.__variable = Var(var_entry, varName)
        self.__type = self.__variable.get_type()

    def get_type(self):  # getType - entries, get_type exp's
        return self.__type  # Type entry

    def get_loc(self):
        return self.__location

    def get_var(self):
        return self.__variable

    def to_string(self):
        return "Field " + varName
