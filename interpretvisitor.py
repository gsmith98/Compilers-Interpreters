# Graham Smith gsmith98@jhu.edu

from visitor import Visitor
from node import *
from box import *
from environment import *

class InterpretVisitor(Visitor):
    def __init__(self, enviro):
        self._stack = []
        self._global_env = enviro
        self._local_env = enviro

    def node_visit(self, host):
        if isinstance(host, ProcedureCall):
            # compute each actual before changing scopes
            actuals = host.get_actuals()
            evaluates = []
            for actual in actuals:
                actual.accept(self)
                eval_act = self._stack.pop()
                evaluates.append(eval_act)

            # make new environment for procedure scope
            old_local = self._local_env
            self._local_env = Environment(host.get_proc().get_scope())

            # put the actuals evaluated values into the environment's boxes
            params = host.get_proc().get_params()
            if len(actuals) > 0:
                boxes = self._local_env.get_boxes()
                for num in range(len(actuals)): # checked earlier for right number
                    target_box = boxes[params[num][0]]
                    assignee = evaluates[num]

                    # copied from Assign
                    if isinstance(target_box, IntegerBox):
                        # assignee is either a number or integerbox
                        if isinstance(assignee, IntegerBox):
                            target_box.set_int(assignee.get_int())
                        else:
                            target_box.set_int(assignee)
                    # else target_box is an array or record
                    else:
                        target_box = assignee # CHANGED!!! PASSED BY REFERENCE, NOT DEEP COPIED

            if host.get_proc().get_instructions() is not None:
                host.get_proc().get_instructions().accept(self)

            self._local_env = old_local

        elif isinstance(host, FunctionCall):
            # compute each actual before changing scopes
            actuals = host.get_actuals()
            evaluates = []
            for actual in actuals:
                actual.accept(self)
                eval_act = self._stack.pop()
                evaluates.append(eval_act)

            # make new environment for procedure scope
            old_local = self._local_env
            self._local_env = Environment(host.get_proc().get_scope())

            # put the actuals evaluated values into the environment's boxes
            params = host.get_proc().get_params()
            if len(actuals) > 0:
                boxes = self._local_env.get_boxes()
                for num in range(len(actuals)): # checked earlier for right number
                    target_box = boxes[params[num][0]]
                    assignee = evaluates[num]

                    # copied from Assign
                    if isinstance(target_box, IntegerBox):
                        # assignee is either a number or integerbox
                        if isinstance(assignee, IntegerBox):
                            target_box.set_int(assignee.get_int())
                        else:
                            target_box.set_int(assignee)
                    # else target_box is an array or record
                    else:
                        target_box = assignee # CHANGED!!! PASSED BY REFERENCE, NOT DEEP COPIED

            if host.get_proc().get_instructions() is not None:
                host.get_proc().get_instructions().accept(self)

            host.get_proc().get_return().accept(self) # evaluate return expression
            # ^ pushes proper thing onto stack

            self._local_env = old_local

        elif isinstance(host, Assign):
            host.get_loc().accept(self)
            host.get_exp().accept(self)

            assignee = self._stack.pop()
            target_box = self._stack.pop()

            if isinstance(target_box, IntegerBox):
                # assignee is either a number or integerbox
                if isinstance(assignee, IntegerBox):
                    target_box.set_int(assignee.get_int())
                else:
                    target_box.set_int(assignee)
            # else target_box is an array or record
            else:
                target_box.assign(assignee)

        elif isinstance(host, If):
            host.get_cond().accept(self)
            boole = self._stack.pop()

            if boole == "True":
                host.get_true().accept(self)
            elif host.get_false() is not None:
                host.get_false().accept(self)

        elif isinstance(host, Repeat):
            host.get_instrs().accept(self)
            while(True):
                host.get_cond().accept(self)
                boole = self._stack.pop()
                if boole == "False":
                    host.get_instrs().accept(self)
                else:
                    break

        elif isinstance(host, Read):
            try:
                inp = int(raw_input())
                host.get_loc().accept(self)
                target_box = self._stack.pop()
                target_box.set_int(inp)
            except EOFError:
                raise CustException("Read input found EOF")
            except ValueError:
                raise CustException("Read could not parse int")

        elif isinstance(host, Write):
            host.get_exp().accept(self)
            writee = self._stack.pop()
            # writee either an integerbox or number
            if isinstance(writee, IntegerBox):
                print writee.get_int()
            else:
                print writee

        elif isinstance(host, Condition):
            host.get_left().accept(self)
            left = self._stack.pop()
            host.get_right().accept(self)
            right = self._stack.pop()
            # left and right are both either numbers or intboxes
            if isinstance(left, IntegerBox):
                num1 = left.get_int()
            else:
                num1 = left
            if isinstance(right, IntegerBox):
                num2 = right.get_int()
            else:
                num2 = right

            rel = host.get_rel()

            if ((rel == "=" and num1 == num2)
                or (rel == "#" and num1 != num2)
                or (rel == "<" and num1 < num2)
                or (rel == ">" and num1 > num2)
                or (rel == ">=" and num1 >= num2)
                or (rel == "<=" and num1 <= num2)):
                self._stack.append("True")
            else:
                self._stack.append("False")

        elif isinstance(host, Number):
            self._stack.append(host.get_value())

        elif isinstance(host, Binary):
            host.get_left().accept(self)
            left = self._stack.pop()
            host.get_right().accept(self)
            right = self._stack.pop()
            # left and right are both either numbers or intboxes
            if isinstance(left, IntegerBox):
                num1 = left.get_int()
            else:
                num1 = left
            if isinstance(right, IntegerBox):
                num2 = right.get_int()
            else:
                num2 = right
             
            op = host.get_op()

            if op == "+":
                num3 = num1 + num2
            elif op == "-":
                num3 = num1 - num2
            elif op == "*":
                num3 = num1 * num2
            elif op == "DIV":
                if num2 == 0:
                    raise CustException("DIV by 0")
                num3 = num1 / num2
            elif op == "MOD":
                if num2 == 0:
                    raise CustException("MOD by 0")
                num3 = num1 % num2

            self._stack.append(num3)

        elif isinstance(host, Var):
            name = host.get_name()
            try:
                push_box = self._local_env.get_box(name)
            except CustException:
                push_box = self._global_env.get_box(name)

            self._stack.append(push_box)

        elif isinstance(host, Index):
            host.get_loc().accept(self)
            array_box = self._stack.pop()
            host.get_exp().accept(self)
            ind = self._stack.pop()
            # ind is either and integerbox or number
            if isinstance(ind, IntegerBox):
                push_box = array_box.get_box(ind.get_int())
            else:
                push_box = array_box.get_box(ind)

            self._stack.append(push_box)

        elif isinstance(host, Field):
            host.get_loc().accept(self)
            rec_box = self._stack.pop()
            var_name = host.get_var().get_name()
            push_box = rec_box.get_box(var_name)
            self._stack.append(push_box)

        # All kinds of host reach this point
        if isinstance(host, Instruction) and host.has_next():
            host.get_next().accept(self)
