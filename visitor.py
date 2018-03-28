# Graham Smith gsmith98@jhu.edu

from entry import *
from scope import *
from node import *


class Visitor(object):
    def visit(self, host):
        pass

    def output(self):
        pass


class textVisitor(Visitor):
    def __init__(self):
        self._indent = 0
        self._s = ""

    def output(self):
        print self._s

    def _spaces(self):
        for num in range(self._indent):
            self._s += " "

    def visit(self, host):
        if isinstance(host, Scope):
            self._spaces()
            self._s += "SCOPE BEGIN\n"
            self._indent += 2

            table = host.getTable()
            for key in sorted(table):
                self._spaces()
                self._s += key + " =>\n"
                self._indent += 2
                table[key].accept(self)  # self is this visitor
                self._indent -= 2

            self._indent -= 2
            self._spaces()
            self._s += "END SCOPE\n"

        elif isinstance(host, Constant):
            self._spaces()
            self._s += "CONST BEGIN\n"
            self._indent += 2
            self._spaces()
            self._s += "type:\n"
            self._indent += 2
            self._spaces()
            self._s += "INTEGER\n"
            self._indent -= 2
            self._spaces()
            self._s += "value:\n"
            self._indent += 2
            self._spaces()
            self._s += str(host.getValue()) + "\n"
            self._indent -= 4
            self._spaces()
            self._s += "END CONST\n"

        elif isinstance(host, Variable):
            self._spaces()
            self._s += "VAR BEGIN\n"
            self._indent += 2
            self._spaces()
            self._s += "type:\n"
            self._indent += 2
            host.getType().accept(self)
            self._indent -= 4
            self._spaces()
            self._s += "END VAR\n"

        elif isinstance(host, Integer):
            self._spaces()
            self._s += "INTEGER\n"

        elif isinstance(host, Array):
            self._spaces()
            self._s += "ARRAY BEGIN\n"
            self._indent += 2
            self._spaces()
            self._s += "type:\n"
            self._indent += 2
            host.getType().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "length:\n"
            self._indent += 2
            self._spaces()
            self._s += str(host.getLength()) + "\n"
            self._indent -= 4
            self._spaces()
            self._s += "END ARRAY\n"

        elif isinstance(host, Record):
            self._spaces()
            self._s += "RECORD BEGIN\n"
            self._indent += 2
            host.getScope().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "END RECORD\n"


# I am borrowing heavily from Peter's posted dot output
class graphVisitor(Visitor):
    def __init__(self):
        self._s = ""
        self.__entries = []

    def output(self):
        print "digraph X { \n" + self._s + "}"

    def visit(self, host):
        if isinstance(host, Scope):
            table = host.getTable()
            temp = ""
            for key in sorted(table):
                theid = table[key].accept(self)
                temp += (key + "_" + str(id(host))
                    + " -> _anchor_" + theid + "\n")

            self._s += "subgraph cluster_" + str(id(host)) + " {\n"
            for key in sorted(table):
                self._s += (key + "_" + str(id(host)) + " [label=\""
                    + key + "\",shape=box,color=white,fontcolor=black]\n")
            self._s += ("_anchor_" + str(id(host))
                + " [label=\"\",style=invis]\n}\n")

            self._s += temp

            return str(id(host))

        elif isinstance(host, Constant):
            typeid = host.getType().accept(self)
            if host not in self.__entries:
                self._s += ("_anchor_" + str(id(host))
                    + " [label=\"" + str(host.getValue())
                    + "\",shape=diamond]\n")
                self.__entries.append(host)
                self._s += ("_anchor_" + str(id(host))
                    + " -> _anchor_" + typeid + "\n")
            return str(id(host))

        elif isinstance(host, Integer):
            if host not in self.__entries:
                self._s += ("_anchor_" + str(id(host))
                    + " [label=\"INTEGER\",shape=box,style=rounded]\n")
                self.__entries.append(host)
            return str(id(host))

        elif isinstance(host, Array):
            typeid = host.getType().accept(self)
            if host not in self.__entries:
                self._s += ("_anchor_" + str(id(host))
                    + " [label=\"Array\\nlength:" + str(host.getLength())
                    + "\",shape=box,style=rounded]\n")
                self.__entries.append(host)
                self._s += ("_anchor_" + str(id(host))
                    + " -> _anchor_" + typeid + "\n")
            return str(id(host))

        elif isinstance(host, Record):
            scopeid = host.getScope().accept(self)
            if host not in self.__entries:
                self._s += ("_anchor_" + str(id(host))
                    + " [label=\"Record\",shape=box,style=rounded]\n")
                self.__entries.append(host)
                self._s += ("_anchor_" + str(id(host))
                    + " -> _anchor_" + scopeid + "\n")
            return str(id(host))

        elif isinstance(host, Variable):
            typeid = host.getType().accept(self)
            if host not in self.__entries:
                self._s += ("_anchor_" + str(id(host))
                    + " [label=\"\",shape=circle]\n")
                self.__entries.append(host)
                self._s += ("_anchor_" + str(id(host))
                    + " -> _anchor_" + typeid + "\n")
            return str(id(host))


class textAstVisitor(textVisitor):
    def __init__(self):
        self._indent = 2
        self._s = "instructions =>\n"

    def output(self):
        print self._s

    def _spaces(self):
        for num in range(self._indent):
            self._s += " "

    def node_visit(self, host):
        if isinstance(host, Assign):
            self._spaces()
            self._s += "Assign:\n"
            self._spaces()
            self._s += "location =>\n"
            self._indent += 2
            host.get_loc().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "expression =>\n"
            self._indent += 2
            host.get_exp().accept(self)
            self._indent -= 2
            if host.has_next():
                host.get_next().accept(self)

        elif isinstance(host, If):
            self._spaces()
            self._s += "If:\n"
            self._spaces()
            self._s += "condition =>\n"
            self._indent += 2
            host.get_cond().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "instructions =>\n"
            self._indent += 2
            host.get_true().accept(self)
            self._indent -= 2

            fals = host.get_false()
            if fals is not None:
                self._spaces()
                self._s += "instructions =>\n"
                self._indent += 2
                fals.accept(self)
                self._indent -= 2

            if host.has_next():
                host.get_next().accept(self)

        elif isinstance(host, Repeat):
            self._spaces()
            self._s += "Repeat:\n"
            self._spaces()
            self._s += "condition =>\n"
            self._indent += 2
            host.get_cond().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "instructions =>\n"
            self._indent += 2
            host.get_instrs().accept(self)
            self._indent -= 2
            if host.has_next():
                host.get_next().accept(self)

        elif isinstance(host, Read):
            self._spaces()
            self._s += "Read:\n"
            self._spaces()
            self._s += "location =>\n"
            self._indent += 2
            host.get_loc().accept(self)
            self._indent -= 2
            if host.has_next():
                host.get_next().accept(self)

        elif isinstance(host, Write):
            self._spaces()
            self._s += "Write:\n"
            self._spaces()
            self._s += "expression =>\n"
            self._indent += 2
            host.get_exp().accept(self)
            self._indent -= 2
            if host.has_next():
                host.get_next().accept(self)

        elif isinstance(host, Condition):
            self._spaces()
            self._s += "Condition (" + host.get_rel() + "):\n"
            self._spaces()
            self._s += "left =>\n"
            self._indent += 2
            host.get_left().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "right =>\n"
            self._indent += 2
            host.get_right().accept(self)
            self._indent -= 2

        elif isinstance(host, Number):
            self._spaces()
            self._s += "Number:\n"
            self._spaces()
            self._s += "value =>\n"
            self._indent += 2
            host.get_const().accept(self)
            self._indent -= 2

        elif isinstance(host, Binary):
            self._spaces()
            self._s += "Binary (" + host.get_op() + "):\n"
            self._spaces()
            self._s += "expression =>\n"
            self._indent += 2
            host.get_left().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "expression =>\n"
            self._indent += 2
            host.get_right().accept(self)
            self._indent -= 2

        elif isinstance(host, Var):
            self._spaces()
            self._s += "Variable:\n"
            self._spaces()
            self._s += "variable =>\n"
            self._indent += 2

            host.get_var().accept(self)
            self._indent -= 2

        elif isinstance(host, Index):
            self._spaces()
            self._s += "Index:\n"
            self._spaces()
            self._s += "location =>\n"
            self._indent += 2
            host.get_loc().accept(self)
            self._indent -= 2
            self._spaces()
            self._s += "expression =>\n"
            self._indent += 2
            host.get_exp().accept(self)
            self._indent -= 2

        elif isinstance(host, Field):
            self._spaces()
            self._s += "Field:\n"
            self._spaces()
            self._s += "location =>\n"
            self._indent += 2
            host.get_loc().accept(self)
            self._indent -= 2
            host.get_var().accept(self)


class graphAstVisitor(Visitor):
    def __init__(self):
        self._s = ""
        self._num = 0

    def output(self):
        print "digraph X { \n" + self._s + "}"

    def __gs(self, number):
        return "N" + str(number)

    def node_visit(self, host):
        this_num = self._num
        this_N = self.__gs(this_num)
        self._num += 1

        if isinstance(host, Assign):
            self._s += this_N + " [label=\":=\",shape=box]\n"

            loc_N = self.__gs(host.get_loc().accept(self))
            self._s += this_N + " -> " + loc_N + " [label=\"location\"]\n"

            exp_N = self.__gs(host.get_exp().accept(self))
            self._s += this_N + " -> " + exp_N + " [label=\"expression\"]\n"

        elif isinstance(host, If):
            self._s += this_N + " [label=\"If\",shape=box]\n"

            cond_N = self.__gs(host.get_cond().accept(self))
            self._s += this_N + " -> " + cond_N + " [label=\"condition\"]\n"

            tru_N = self.__gs(host.get_true().accept(self))
            self._s += this_N + " -> " + tru_N + " [label=\"true\"]\n"

            if host.has_false():
                fals_N = self.__gs(host.ger_false().accept(self))
                self._s += this_N + " -> " + fals_N + " [label=\"false\"]\n"

        elif isinstance(host, Repeat):
            self._s += this_N + " [label=\"Repeat\",shape=box]\n"

            cond_N = self.__gs(host.get_cond().accept(self))
            self._s += this_N + " -> " + cond_N + " [label=\"condition\"]\n"

            instrs_N = self.__gs(host.get_instrs().accept(self))
            self._s += (this_N + " -> " + instrs_N +
                " [label=\"instructions\"]\n")

        elif isinstance(host, Read):
            self._s += this_N + " [label=\"Read\",shape=box]\n"

            loc_N = self.__gs(host.get_loc().accept(self))
            self._s += this_N + " -> " + loc_N + " [label=\"location\"]\n"

        elif isinstance(host, Write):
            self._s += this_N + " [label=\"Write\",shape=box]\n"

            exp_N = self.__gs(host.get_exp().accept(self))
            self._s += this_N + " -> " + exp_N + " [label=\"expression\"]\n"

        elif isinstance(host, Condition):
            rel = host.get_rel()
            self._s += this_N + " [label=\"" + rel + "\",shape=box]\n"

            left_N = self.__gs(host.get_left().accept(self))
            self._s += this_N + " -> " + left_N + " [label=\"left\"]\n"

            right_N = self.__gs(host.get_right().accept(self))
            self._s += this_N + " -> " + right_N + " [label=\"right\"]\n"

        elif isinstance(host, Number):
            self._s += this_N + " [label=\"Number\",shape=box]\n"
            const_N = self.__gs(self._num)
            self._num += 1
            val = str(host.get_value())
            self._s += const_N + " [label=\"" + val + "\",shape=diamond]\n"

            self._s += this_N + " -> " + const_N + " [label=\"ST\"]\n"

        elif isinstance(host, Binary):
            op = host.get_op()
            self._s += this_N + " [label=\"" + op + "\",shape=box]\n"

            left_N = self.__gs(host.get_left().accept(self))
            self._s += this_N + " -> " + left_N + " [label=\"left\"]\n"

            right_N = self.__gs(host.get_right().accept(self))
            self._s += this_N + " -> " + right_N + " [label=\"right\"]\n"

        elif isinstance(host, Var):
            self._s += this_N + " [label=\"Variable\",shape=box]\n"

            var_N = self.__gs(self._num)
            self._num += 1
            name = str(host.get_name())
            self._s += var_N + " [label=\"" + name + "\",shape=circle]\n"

            self._s += this_N + " -> " + var_N + " [label=\"ST\"]\n"

        elif isinstance(host, Index):
            self._s += this_N + " [label=\"Index\",shape=box]\n"

            loc_N = self.__gs(host.get_loc().accept(self))
            self._s += this_N + " -> " + loc_N + " [label=\"location\"]\n"

            exp_N = self.__gs(host.get_exp().accept(self))
            self._s += this_N + " -> " + exp_N + " [label=\"expression\"]\n"

        elif isinstance(host, Field):
            self._s += this_N + " [label=\"Field\",shape=box]\n"

            loc_N = self.__gs(host.get_loc().accept(self))
            self._s += this_N + " -> " + loc_N + " [label=\"location\"]\n"

            var_N = self.__gs(host.get_var().accept(self))
            self._s += this_N + " -> " + var_N + " [label=\"variable\"]\n"

        # All kinds of host reach this point
        if isinstance(host, Instruction) and host.has_next():
            next_N = self.__gs(host.get_next().accept(self))
            self._s += this_N + " -> " + next_N + " [label=\"next\"]\n"
            self._s += "{rank=same; " + this_N + " " + next_N + "}\n"

        return this_num
