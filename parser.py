#Graham Smith gsmith98@jhu.edu

from customexception import *
from token import *
from observer import *
from entry import *
from scope import *
from node import *
from ir import IR


class Parser:

    def __init__(self, list_of_toks, signal):
        self.__tok_list = list_of_toks
        self.__c = 0  # counter for position to be incremented
        self.__curr = self.__tok_list[self.__c]
        self.__obslist = []
        self.__sem = False
        self.__ast = False
        if signal > 1:
            self.__sem = True  # if sem is true, do -t semantic analysis
        if signal > 2:
            self.__ast = True  # if ast is true do -a stuff
        self.__currScope = None

    def addObserver(self, obs):
        if obs not in self.__obslist:
            self.__obslist.append(obs)

    def removeObserver(self, obs):
        if obs in self.__obslist:
            self.__obslist.remove(obs)

    # DECORATOR FOR FUNCTIONS
    # Notifies all observers when entering/leaving function
    def decfunc(func):
        def wrapfunc(self, *arg):
            for obs in self.__obslist:
                obs.notifyStart(func.__name__)

            thing = func(self, *arg)
            # functions with no return actually return None

            for obs in self.__obslist:
                obs.notifyEnd()

            return thing
        return wrapfunc

    def parse(self):
        if self.__sem:
            universe = Scope(None)
            universe.insert("INTEGER", Integer())
            proScope = Scope(universe)
            self.__currScope = proScope

        tree = self.__Program()

        if self.__sem:
            int_rep = IR()
            int_rep.st_scope = proScope
            if self.__ast:
                int_rep.ast_tree = tree
            return int_rep

    #  takes list of possible current tokens
    #  returns the token encountered, errors otherwise
    def __match(self, str_list):
        if self.__curr.kind in str_list:
            tok = self.__gobble()

            for obs in self.__obslist:
                obs.notifyMatch(tok)

            return tok
        else:
            raise CustException(self.__Xstring(str_list, self.__curr))

    #  skip over current token (should be output). returns what it ate
    def __gobble(self):
        # SOME FORM OF OUTPUT
        eaten = self.__curr
        self.__c += 1
        self.__curr = self.__tok_list[self.__c]
        return eaten

    def __Xstring(self, str_list, tok):
        return ("Expected " + str(str_list) + " @"
            + str(tok.start_position) + ", found " + tok.kind)

    @decfunc
    def __Program(self):
        self.__match("PROGRAM")

        start_tok = self.__match("identifier")

        self.__match(";")
        self.__Declarations()
        tree = None
        if self.__curr.kind == "BEGIN":
            self.__match("BEGIN")
            tree = self.__Instructions()

        self.__match("END")

        end_tok = self.__match("identifier")

        if self.__sem and start_tok.value != end_tok.value:
            raise CustException("Program " + start_tok.value +
                " and End " + end_tok.value + " don't match")

        self.__match(".")
        if self.__curr.kind != "eof":
            raise CustException(self.__Xstring("eof", self.__curr))

        if self.__ast:
            return tree  # could be none if program has no BEGIN

    @decfunc
    def __Declarations(self):  # nothing at all is a valid Declarations
        while True:            # so we can't match or raise errors
            if self.__curr.kind == "CONST":
                self.__ConstDecl()
            elif self.__curr.kind == "TYPE":
                self.__TypeDecl()
            elif self.__curr.kind == "VAR":
                self.__VarDecl()
            elif self.__curr.kind == "PROCEDURE":
                self.__ProcDecl()
            else:
                break

    @decfunc
    def __ConstDecl(self):
        self.__match("CONST")
        while self.__curr.kind == "identifier":
            name_tok = self.__match("identifier")
            self.__match("=")
            exp = self.__Expression()
            self.__match(";")

            num = 5
            if self.__ast:
                if not isinstance(exp, Number):
                    raise CustException("Value could not be folded")
                num = exp.get_value()

            if self.__sem:
                new_const = Constant(Integer(), num)
                self.__currScope.insert(name_tok.value, new_const)

    @decfunc
    def __TypeDecl(self):
        self.__match("TYPE")
        while self.__curr.kind == "identifier":
            name_tok = self.__match("identifier")
            self.__match("=")
            type_entry = self.__Type()
            self.__match(";")

            if self.__sem:
                self.__currScope.insert(name_tok.value, type_entry)

    @decfunc
    def __ProcDecl(self):
        out_scope = self.__currScope
        self.__currScope = Scope(out_scope)

        self.__match("PROCEDURE")
        name_tok = self.__match("identifier")
        self.__match("(")
        params = []
        if self.__curr.kind != ")":
            params = self.__Formals()
        self.__match(")")
        proc_kind = "procedure"
        if self.__curr.kind == ":":
            proc_kind = "function"
            self.__match(":")
            ret_typ = self.__Type()
            if not isinstance(ret_typ, Integer):
                raise CustException("Function return type must be integer")
        self.__match(";")

        # prelim entry in symbol table for recursion
        if self.__sem:
            if proc_kind == "procedure":
                out_scope.insert(name_tok.value, Procedure(params, None, None))
            else:
                out_scope.insert(name_tok.value, Function(params, None, None, None, ret_typ))

        while self.__curr.kind == "VAR":
            self.__VarDecl()
        instrs = None
        if self.__curr.kind == "BEGIN":
            self.__match("BEGIN")
            instrs = self.__Instructions()
        if proc_kind == "function":
            self.__match("RETURN")
            exp = self.__Expression()
            if exp.get_type() is not ret_typ:
                raise CustException("Return type does not match function type")
        self.__match("END")
        end_tok = self.__match("identifier")
        self.__match(";")

        if name_tok.value != end_tok.value:
            raise CustException("Incorrect identifer used in procedure END statement")

        proc_scope = self.__currScope
        self.__currScope = out_scope

        if self.__sem:
            self.__currScope.find(name_tok.value).give_scope(proc_scope)
            self.__currScope.find(name_tok.value).give_instructions(instrs)
            if proc_kind == "function":
                self.__currScope.find(name_tok.value).give_return(exp)

    @decfunc
    def __Formals(self):
        params = []
        params.extend(self.__Formal())
        while self.__curr.kind == ";":
            self.__match(";")
            params.extend(self.__Formal())
        return params

    @decfunc
    def __Formal(self):
        nameList = self.__IdentifierList()
        self.__match(":")
        type_entry = self.__Type()

        if self.__sem:
            for name in nameList:
                self.__currScope.insert(name, Variable(type_entry))

        return_params = []
        for name in nameList:
            return_params.append((name, type_entry)) # list of tuples
        return return_params

    @decfunc
    def __VarDecl(self):
        self.__match("VAR")
        while self.__curr.kind == "identifier":
            nameList = self.__IdentifierList()
            self.__match(":")
            type_entry = self.__Type()
            self.__match(";")

            if self.__sem:
                for name in nameList:
                    self.__currScope.insert(name, Variable(type_entry))

    @decfunc
    def __Type(self):
        # LONE IDENTIFIER CASE----------------------
        if self.__curr.kind == "identifier":
            name_tok = self.__match("identifier")

            if self.__sem:
                type_entry = self.__currScope.find(name_tok.value)
                if type_entry is None:
                    raise CustException(name_tok.value
                        + " not declared before used")
                elif not isinstance(type_entry, Type):
                    raise CustException(name_tok.value + " is not a Type")

                return type_entry
            # else return None implied (for when sem is false)

        # ARRAY CASE--------------------------------
        elif self.__curr.kind == "ARRAY":
            self.__match("ARRAY")
            exp = self.__Expression()
            self.__match("OF")
            type_entry = self.__Type()
            # ^^the recursive Type() call will raise error if there are any

            num = 5
            if self.__ast:
                if not isinstance(exp, Number):
                    raise CustException("Array length could not be folded")
                if exp.get_value() < 1:
                    raise CustException("Array length "
                        + exp.get_value() + " < 1")
                num = exp.get_value()

            if self.__sem:
                return Array(type_entry, num)

        # RECORD CASE-------------------------------
        elif self.__curr.kind == "RECORD":
            self.__match("RECORD")

            if self.__sem:
                new_scope = Scope(self.__currScope)
                return_scope = self.__currScope
                self.__currScope = new_scope

            while self.__curr.kind == "identifier":
                nameList = self.__IdentifierList()
                self.__match(":")
                type_entry = self.__Type()
                self.__match(";")

                if self.__sem:
                    for name in nameList:
                        self.__currScope.insert(name, Variable(type_entry))

            self.__match("END")

            if self.__sem:
                self.__currScope.sever()
                new_record = Record(self.__currScope)
                self.__currScope = return_scope
                return new_record

        # NOT IDENTIFIER ARRAY OR RECORD CASE--------
        else:
            possible = ["identifier", "ARRAY", "RECORD"]
            raise CustException(self.__Xstring(possible, self.__curr))

    @decfunc
    def __Expression(self):
        prefix = None
        if self.__curr.kind in ["+", "-"]:
            prefix = self.__match(["+", "-"])
        prior = self.__Term()
        while self.__curr.kind in ["+", "-"]:
            op = self.__match(["+", "-"])
            latter = self.__Term()
            if self.__ast:
                bina = Binary(op.kind, prior, latter)
                # ^binary /folded number node
                prior = bina
        if self.__ast:
            if prefix is not None and prefix.kind == "-":  # 0 - (expression)
                bina = Binary("-", Number(Constant(Integer(), 0)), prior)
                prior = bina
            return prior

    @decfunc
    def __Term(self):
        prior = self.__Factor()
        while self.__curr.kind in ["*", "DIV", "MOD"]:
            op = self.__match(["*", "DIV", "MOD"])
            latter = self.__Factor()
            if self.__ast:
                bina = Binary(op.kind, prior, latter)
                # ^binary /folded number node
                prior = bina
        if self.__ast:
            return prior

    @decfunc
    def __Factor(self):
        if self.__curr.kind == "integer":
            num = self.__match("integer")
            if self.__ast:
                return Number(Constant(Integer(), num.value))
        elif self.__curr.kind == "identifier":
            if isinstance(self.__currScope.find(self.__curr.value), Function):
                func = self.__Call()
                if self.__ast:
                    return func
            elif isinstance(self.__currScope.find(self.__curr.value), Procedure):
                raise CustException("Procedure without return type cannot be an expression")
            else:
                desig = self.__Designator()
                if self.__ast:
                    return desig
        elif self.__curr.kind == "(":
            self.__match("(")
            exp = self.__Expression()
            self.__match(")")
            if self.__ast:
                return exp
        else:
            possible = ["integer", "identifier", "("]
            raise CustException(self.__Xstring(possible, self.__curr))

    @decfunc
    def __Instructions(self):
        first = self.__Instruction()
        prior = first
        while self.__curr.kind == ";":
            self.__match(";")
            latter = self.__Instruction()

            if self.__ast:
                prior.give_next(latter)
                prior = latter

        if self.__ast:
            return first

    @decfunc
    def __Instruction(self):
        a = self.__curr.kind  # save myself from writing it 10 time right now
        if a == "identifier":
            if isinstance(self.__currScope.find(self.__curr.value), Procedure):
                return self.__Call()
            elif isinstance(self.__currScope.find(self.__curr.value), Function):
                raise CustException("Procedure with a return type cannot be an instruction")
            else:
                return self.__Assign()
        elif a == "IF":
            return self.__If()
        elif a == "REPEAT":
            return self.__Repeat()
        elif a == "WHILE":
            return self.__While()
        elif a == "READ":
            return self.__Read()
        elif a == "WRITE":
            return self.__Write()
        else:
            possible = ["identifier", "IF", "REPEAT", "WHILE", "READ", "WRITE"]
            raise CustException(self.__Xstring(possible, self.__curr))

    @decfunc
    def __Call(self):
        proc_tok = self.__match("identifier")
        self.__match("(")
        actuals = []
        if self.__curr.kind != ")":
            actuals = self.__ExpressionList()
        self.__match(")")

        proc_ent = self.__currScope.find(proc_tok.value)
        if len(actuals) != len(proc_ent.get_params()):
            raise CustException("Wrong number of arguments to " + proc_tok.value)        
        for num in range(len(actuals)):
            if actuals[num].get_type() is not proc_ent.get_params()[num][1]:
                raise CustException("Incorrect argument typing for " + proc_tok.value)

        if isinstance(proc_ent, Procedure):
            return ProcedureCall(proc_ent, actuals)
        else:
            return FunctionCall(proc_ent, actuals)

    @decfunc
    def __Assign(self):
        loc = self.__Designator()
        self.__match(":=")
        exp = self.__Expression()

        if self.__ast:
            if not (isinstance(loc, Var) or isinstance(loc, Index)
                or isinstance(loc, Field)):  # Arrays/records hold variables
                raise CustException("Can only assign to variables")
            if loc.get_type() is not exp.get_type():
                raise CustException(
                    "Assign type mismatch- not occurrence equivalent")

            return Assign(loc, exp)  # Node

    @decfunc
    def __If(self):
        self.__match("IF")
        cond = self.__Condition()
        self.__match("THEN")
        tru = self.__Instructions()
        if self.__curr.kind == "ELSE":
            self.__match("ELSE")
            fals = self.__Instructions()
        else:
            fals = None
        self.__match("END")

        if self.__ast:
            return If(cond, tru, fals)  # Node

    @decfunc
    def __Repeat(self):
        self.__match("REPEAT")
        instrs = self.__Instructions()
        self.__match("UNTIL")
        cond = self.__Condition()
        self.__match("END")

        if self.__ast:
            return Repeat(cond, instrs)  # Node

    @decfunc
    def __While(self):
        self.__match("WHILE")
        cond = self.__Condition()
        self.__match("DO")
        instrs = self.__Instructions()
        self.__match("END")

        if self.__ast:
            rep = Repeat(cond.negate(), instrs)
            return If(cond, rep)  # turn while into if + repeat

    @decfunc
    def __Condition(self):
        left = self.__Expression()  # programming is my self expression
        relation = self.__match(["=", "#", "<", ">", "<=", ">="])
        right = self.__Expression()  # express yourself! :D

        if self.__ast:
            if not (isinstance(left.get_type(), Integer)
                and isinstance(right.get_type(), Integer)):
                raise CustException("Cannot compare non-integers")

            return Condition(relation.kind, left, right)  # node

    @decfunc
    def __Write(self):
        self.__match("WRITE")
        exp = self.__Expression()

        if self.__ast:
            if not isinstance(exp.get_type(), Integer):
                raise CustException("Can only Write integers")

            return Write(exp)  # Node

    @decfunc
    def __Read(self):
        self.__match("READ")
        loc = self.__Designator()

        if self.__ast:
            if (not (isinstance(loc, Var)
                or isinstance(loc, Index)
                or isinstance(loc, Field))
                or not isinstance(loc.get_type(), Integer)):
                raise CustException("Can only Read into an integer variable")

            return Read(loc)  # Node

    @decfunc
    def __Designator(self):
        ident_tok = self.__match("identifier")
        ident = None
        if self.__ast:
            ent = self.__currScope.find(ident_tok.value)
            if ent is None:
                raise CustException(ident_tok.value + " not declared in scope")

            if isinstance(ent, Type):
                raise CustException(
                    "A designator can't start with a or be a type.")

            ident = Var(ent, ident_tok.value)
            # ^ent is variable entry: Var node object holding ent
            # ^ent is Constant entry: (like sz = 8) Var makes a Number node

        return self.__Selector(ident)

    @decfunc
    def __Selector(self, ident):  # nothing at all would be a valid Selector
        prior = ident
        while True:
            if self.__curr.kind == "[":
                self.__match("[")
                exp_list = self.__ExpressionList()
                self.__match("]")

                if self.__ast:
                    for exp in exp_list:
                        prior = Index(prior, exp)

            elif self.__curr.kind == ".":
                self.__match(".")
                name_tok = self.__match("identifier")

                if self.__ast:
                    prior = Field(prior, name_tok.value)
            else:
                if self.__ast:
                    return prior
                break

    @decfunc
    def __IdentifierList(self):
        nameList = []
        name_tok = self.__match("identifier")
        nameList.append(name_tok.value)
        while self.__curr.kind == ",":
            self.__match(",")
            name_tok = self.__match("identifier")
            nameList.append(name_tok.value)

        return nameList

    @decfunc
    def __ExpressionList(self):
        exp_list = []
        exp_list.append(self.__Expression())
        while self.__curr.kind == ",":
            self.__match(",")
            exp_list.append(self.__Expression())
        if self.__ast:
            return exp_list
