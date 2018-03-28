# Graham Smith gsmith98@jhu.edu

from visitor import Visitor
from node import *
from box import *


class XGenerateVisitor(Visitor):
    def __init__(self, scop):
        self._stack = []
        self._scope = scop
        self._label_num = 0

        self._s = ("            .data\n" +
                   "int_new:    .asciz \"%d\\n\"\n" +
                   "            .align 2\n" +
                   "int_scan:   .asciz \"%d\"\n" +
                   "            .align 2\n" +
                   "ind_err:    .asciz \"error: index out of bounds\\n\"\n" +
                   "            .align 2\n" +
                   "z_err:      .asciz \"error: DIV or MOD by zero\\n\"\n" +
                   "            .align 2\n")

        if scop.get_size() > 0:
            self._s += "vars:       .space   " + str(scop.get_size()) + "\n\n"
        else:
            self._s += "vars:\n\n"
                    
        self._s += ("            .text\n" +
                   "            .globl  main\n" +
                   "main:\n" +
                   "            .ent    main\n" +
                   "            .frame  $sp, 32, $ra\n" +
                   "            .set    noreorder\n" +
                   "            .cpload $t9\n" +
                   "            .set    reorder\n" +
                   "            subu    $sp, $sp, 32\n" +
                   "            .cprestore 16\n" +
                   "            sw      $ra, 28($sp)\n\n" +
                   "            move    $s8, $sp\n" +
                   "            la      $s0, vars\n\n")
        # $s0 reserved for vars pointer
        # $s1-$s7 are the register stack
        # $s8 IS THE FRAME POINTER

        scop.give_offsets()

        self._instack = 0 # num of things in stack

    # thing to push in register $a0
    # doesn't trash t registers
    def _push(self):
        self._s += "            # PUSH\n"
        if self._instack < 7:
            self._instack += 1
            self._s += "            move    $s" + str(self._instack) + ", $a0\n"
        else:
            self._instack += 1
            top = self._instack % 7
            self._s += ("            sub     $sp, 4\n" +
                        "            sw      $s" + str(top) + ", 0($sp)\n" +
                        "            move    $s" + str(top) + ", $a0\n")
        self._s += "            # END PUSH\n"


    # pops result into register $v0
    # doesn't trash t registers
    def _pop(self):
        self._s += "            # POP\n"
        if self._instack <= 7:
            self._s += "            move    $v0, $s" + str(self._instack) + "\n"
            self._instack -= 1
        else:
            top = self._instack % 7
            self._s += ("            move    $v0, $s" + str(top) + "\n" +
                        "            lw      $s" + str(top) + ", 0($sp)\n" +
                        "            add     $sp, 4\n")
            self._instack -= 1
        self._s += "            # END POP\n"


    def output(self):
        self._s += ("            jal     exit\n" +
                    "            .end    main\n\n\n" +
                    "            .globl  deep_copy\n" +
                    "deep_copy:\n" + # $a0 target addr, $a1 size, $a2 source addr
                    "            .ent    deep_copy\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +    
                    "deep_loop:\n" +
                    "            lw      $t0, 0($a2)\n" +
                    "            sw      $t0, 0($a0)\n" +
                    "            addi    $a0, 4\n" +
                    "            addi    $a2, 4\n" +
                    "            addi    $a1, -4\n" +
                    "            bnez    $a1, deep_loop\n" +
                    "            .cprestore 16\n" +
                    "            jr      $ra\n" +
                    "            .end    deep_copy\n\n" +
                    "            .globl  eq\n" +
                    "eq:\n" + # args a0, a1 to compare
                    "            .ent    eq\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            beq     $a0, $a1, eqt\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "eqt:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    eq\n\n" +
                    "            .globl  neq\n" +
                    "neq:\n" + # args a0, a1 to compare
                    "            .ent    neq\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            bne     $a0, $a1, neqt\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "neqt:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    neq\n\n" +
                    "            .globl  lt\n" +
                    "lt:\n" + # args a0, a1 to compare
                    "            .ent    lt\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            blt     $a0, $a1, ltt\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "ltt:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    lt\n\n" +
                    "            .globl  gt\n" +
                    "gt:\n" + # args a0, a1 to compare
                    "            .ent    gt\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            bgt     $a0, $a1, gtt\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "gtt:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    gt\n\n" +
                    "            .globl  gte\n" +
                    "gte:\n" + # args a0, a1 to compare
                    "            .ent    gte\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            bge     $a0, $a1, gtet\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "gtet:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    gte\n\n" +
                    "            .globl  lte\n" +
                    "lte:\n" + # args a0, a1 to compare
                    "            .ent    lte\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            ble     $a0, $a1, ltet\n" +
                    "            # false\n" +
                    "            li      $a0, 0\n")
        self._s += ("            jr      $ra\n" +
                    "ltet:        #true\n" +
                    "            li      $a0, 1\n")
        self._s += ("            jr      $ra\n" +
                    "            .end    lte\n\n" +
                    "            .globl  ind_check\n" +
                    "ind_check:\n" + # $a0 is index, $a1 is max index
                    "            .ent    ind_check\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" +
                    "            .cprestore 16\n" +
                    "            bltz    $a0, bad_ind\n" +
                    "            bgt     $a0, $a1, bad_ind\n" +
                    "            jr      $ra\n" +
                    "bad_ind:\n" +
                    "            # Dont bother saving ra to stack, won't need it\n" +
                    "            la      $a0, ind_err\n" +
                    "            jal     printf\n" +
                    "            jal     exit\n" +
                    "            .end    ind_check\n\n" +
                    "            .globl  check_z\n" +
                    "check_z:\n" + # $a0 is number to check if zero
                    "            .ent    check_z\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" + 
                    "            .cprestore 16\n" +
                    "            beqz    $a0, bad_z\n" +
                    "            jr      $ra\n" +
                    "bad_z:\n" +
                    "            # Dont bother saving ra to stack, won't need it\n" +
                    "            la      $a0, z_err\n" +
                    "            jal     printf\n" +
                    "            jal     exit\n\n" +
                    "            .end    check_z\n\n" +
                    "            .globl  exit\n" +
                    "exit:\n" +
                    "            .ent    exit\n" +
                    "            .frame  $sp, 32, $ra\n" +
                    "            .set    noreorder\n" +
                    "            .cpload $t9\n" +
                    "            .set    reorder\n\n" + 
                    "            subu    $sp, $sp, 32\n" +
                    "            .cprestore 16\n" +
                    "            move    $sp, $s8\n" + # reset stack pointer
                    "            lw      $ra, 28($sp)\n" +
                    "            addi    $sp, 32\n" +
                    "            jr      $ra\n" +
                    "            .end    exit\n")
                   
 

        return self._s

    def node_visit(self, host):
        if isinstance(host, Assign):
            self._s += "#FIND THE OFFSET OF THE THING TO ASSIGN TO\n"
            host.get_loc().accept(self)
            host.get_exp().accept(self) 
            self._pop()
            # $v0 is either a number to be assigned
            # or the offset of the memory holding an integer, array, or record to be assigned
            if not isinstance(host.get_exp(), Location):
                self._s += "            move    $t1, $v0\n" # t1 holds the number to be assigned
                self._pop()
                # v0 holds offset of location to assign to
                self._s += ("            add     $t0, $v0, $s0\n" + # $t0 holds address of target
                            "            sw      $t1, 0($t0)\n\n") # store num at target address
            else:
                sz = host.get_loc().get_type().get_size() # sz of thing being assigned to
 
                self._s += "            add    $a2, $v0, $s0\n" # a2 holds address of source
                self._pop()
                self._s += ("            add     $a0, $v0, $s0\n" + # a0 holds address of target
                            "            li      $a1, " + str(sz) + "\n" + # $a1 holds target size
                            "            jal     deep_copy\n\n")

        elif isinstance(host, If):
            host.get_cond().accept(self)
            self._pop()
            # v0 has 0 or 1
            Lnum = self._label_num
            self._label_num += 1

            # Lnum used to skip true stuff, Lnum2 to skip false (if any)

            self._s += "            beqz    $v0, L" + str(Lnum) + "\n"

            host.get_true().accept(self) # make true instrs

            if host.has_false():
                Lnum2 = self._label_num
                self._label_num +=1

                self._s += ("            b       L" + str(Lnum2) + "\n" +
                            "L" + str(Lnum) + ":\n")

                host.get_false().accept(self) # make false instrs

                self._s += "L" + str(Lnum2) + ":\n\n"
            else:
                self._s += "L" + str(Lnum) + ":\n\n"

        elif isinstance(host, Repeat):
            Lnum = self._label_num
            self._label_num += 1

            self._s += "L" + str(Lnum) + ":\n"

            host.get_instrs().accept(self) # make instrs in repeat loop

            host.get_cond().accept(self)
            self._pop()
            # at this point 0 or 1 (F/T) is in $v0
            self._s += "            beqz    $v0, L" + str(Lnum) + "\n\n"

        elif isinstance(host, Read):
            host.get_loc().accept(self)
            self._pop()
            # $v0 now holds the offset of the address to read into
            self._s += ("            add     $a1, $v0, $s0\n" + # a1 the address to read into
                        "            la      $a0, int_scan\n" + # %d int designator
                        "            jal     scanf\n\n")

        elif isinstance(host, Write):
            host.get_exp().accept(self)
            self._pop()

            # $v0 is now either the integer to write
            # or the offset of the memory address holding the integer
            if isinstance(host.get_exp(), Location): 
                self._s += ("            add     $t0, $v0, $s0 #write\n" + # $t0 is address of int
                            "            lw      $v0, 0($t0)\n") # $t1 is now int's value

            # $v0 is now the int to be written in either case               
            self._s += ("            move    $a1, $v0\n" +
                        "            la      $a0, int_new\n" +
                        "            jal     printf\n\n")

        elif isinstance(host, Condition):
            rel = host.get_rel()
            host.get_left().accept(self)
            host.get_right().accept(self)

            # RIGHT
            self._pop()
            # $v0 either holds a number or an address where an int is       
            if isinstance(host.get_right(), Location): # offset
                self._s += ("            add     $t0, $v0, $s0 #cond2\n" + # $t0 is now address of num1
                            "            lw      $a1, 0($t0)\n")    # $t1 is now the num
            else:
                self._s += "            move    $a1, $v0\n"
            # $a1 is now a num in either case

            # LEFT
            self._pop()
            # $v0 either holds a number or an address where an int is
            if isinstance(host.get_left(), Location): # offset
                self._s += ("            add     $t0, $v0, $s0 #cond1\n" + # $t0 is now address of num1
                            "            lw      $a0, 0($t0)\n")    # $t2 is now the num
            else:
                self._s += "            move    $a0, $v0\n"
            # $a0 is now a num in either case

            # $a0 now holds num1, $a1 holds num2
            if rel == "=":
                self._s += "            jal     eq\n\n"
            elif rel == "#":
                self._s += "            jal     neq\n\n"
            elif rel == "<":
                self._s += "            jal     lt\n\n"
            elif rel == ">":
                self._s += "            jal     gt\n\n"
            elif rel == ">=":
                self._s += "            jal     gte\n\n"
            elif rel == "<=":
                self._s += "            jal     lte\n\n"

            self._push()

        elif isinstance(host, Number):
            num = host.get_value()
            if num < -(2**31) or num > ((2**31) - 1):
                raise CustException("Value " + str(num) + " won't fit in a 32 bit register")

            self._s += "            li      $a0, " + str(num) + "\n"
            self._push()

        elif isinstance(host, Binary):
            op = host.get_op()
            host.get_left().accept(self)
            host.get_right().accept(self)

            self._pop()
            # RIGHT
            # $v0 either holds a number or an address where an int is       
            if isinstance(host.get_right(), Location): # offset
                self._s += ("            add     $t0, $v0, $s0\n" + # $t0 is now address of num1
                            "            lw      $t1, 0($t0)\n")    # $11 is now the num
            else:
                self._s += "            move    $t1, $v0\n"
            # $t1 is now num2 in either case

            # LEFT
            self._pop()
            # $v0 either holds a number or an address where an int is
            if isinstance(host.get_left(), Location): # offset
                self._s += ("            add     $t2, $v0, $s0\n" + # $t2 is now address of num1
                            "            lw      $t0, 0($t2)\n")    # $t0 is now the num
            else:
                self._s += "            move    $t0, $v0\n"
            # $to is now num1 in either case

            # $t0 now holds num1, $t1 holds num2
            if op == "+":
                self._s += "            add     $a0, $t0, $t1\n\n"
            elif op == "-":
                self._s += "            sub     $a0, $t0, $t1\n\n"
            elif op == "*":
                self._s += ("            mult    $t0, $t1\n" +
                            "            mflo    $a0\n\n")
            elif op == "DIV":
                self._s += ("            move    $a0, $t1\n" +
                            "            jal     check_z\n" +
                            "            div     $t0, $t1\n" +
                            "            mflo    $a0\n\n")

            elif op == "MOD":
                self._s += ("            move    $a0, $t1\n" +
                            "            jal     check_z\n" +
                            "            div     $t0, $t1\n" +
                            "            mfhi    $a0\n\n")

            self._push()

        elif isinstance(host, Var):
            ent_off = host.get_var().get_address()
            self._s += "            li      $a0, " + str(ent_off) + "\n"
            self._push()

        elif isinstance(host, Index):
            self._s += "# fetching offset of the array\n"
            host.get_loc().accept(self)

            arr_ent = host.get_loc().get_type()
            max_ind = arr_ent.getLength() - 1
            elem_size = arr_ent.getType().get_size()

            host.get_exp().accept(self)
            self._pop()
            # $v0 is either the integer index
            # or the offset of the memory address holding the integer index
            if isinstance(host.get_exp(), Location): # offset
                self._s += ("            add     $t0, $v0, $s0 # was a location\n" + # $t0 is now address of index
                            "            lw      $a0, 0($t0)\n")    # $11 is now the index
            else:
                self._s += "            move    $a0, $v0\n"
            # $a0 now definitely holds the index int in either case
            self._pop()
            # v0 now holds offset of array
            self._s += ("            move    $t2, $v0\n" +
                        "            li      $a1, " + str(max_ind) + "\n" +
                        "            jal     ind_check\n" +
                        "            li      $t0, " + str(elem_size) + "\n" +
                        "            mult    $a0, $t0\n" +
                        "            mflo    $t1\n" + # t1 is now the offset within the array
                        "            add     $a0, $t1, $t2\n\n") # array offset + index offset
            self._push()

        elif isinstance(host, Field):
            host.get_loc().accept(self)
            # offset of this location is in stack
            host.get_var().accept(self)
            self._pop()
            # $v0 now holds offset of the variable (within the record)
            self._s += "            move    $t0, $v0\n"
            self._pop()
            self._s += "            add     $a0, $t0, $v0\n\n"
            # a0 now holds the total offset of this field of the array
            self._push()

        if isinstance(host, Instruction) and host.has_next():
            host.get_next().accept(self)
