#!/usr/bin/python

import sys
from customexception import CustException
from scanner import Scanner
from parser import Parser
from observer import *
from visitor import *
from ir import IR
from environment import *
from box import *
from interpretvisitor import *
from generatevisitor import *
from xgeneratevisitor import *


def main():
    try:
        flags = {"-s": False, "-c": False, "-t": False, "-a": False,
            "-i": False, "-g": False, "-x": False, "file": False}
        scan_start = False

        usage(flags)

        source = get_source(flags)

        # SCANNER PHASE --------------
        my_scan = Scanner(source)
        part_toks = []
        scan_start = True
        # ^^prevents partial list being printed when error b4 scanner

        full_toks = my_scan.all(part_toks)
        # ^^lists mutable: part_toks will be changed until error

        if flags["-s"]:
            print ''
            for tok in full_toks:
                print tok.to_string()
            sys.exit()

        # PARSER PHASE ---------------
        observers = []
        if flags["-c"] and not flags["-g"]:
            observers.append(textObserver())
        elif flags["-c"] and flags["-g"]:
            observers.append(graphicalObserver())

        if flags["-c"]:
            signal = 1
        elif flags["-t"]:
            signal = 2
        else:
            signal = 3

        my_parse = Parser(full_toks, signal)

        for obs in observers:
            my_parse.addObserver(obs)

        # V an intermediate representation object
        int_rep = my_parse.parse()
        pro_scope = int_rep.st_scope
        tree_node = int_rep.ast_tree

        # -c output
        for obs in observers:
            obs.output()

        # -t and -a output
        if flags["-t"] and not flags["-g"]:
            tv = textVisitor()
            pro_scope.accept(tv)
            tv.output()
        elif flags["-t"] and flags["-g"]:
            gv = graphVisitor()
            pro_scope.accept(gv)
            gv.output()
        elif flags["-a"] and not flags["-g"] and tree_node is not None:
            tav = textAstVisitor()
            tree_node.accept(tav)
            tav.output()
        elif flags["-a"] and flags["-g"] and tree_node is not None:
            gav = graphAstVisitor()
            tree_node.accept(gav)
            gav.output()

        if flags["-c"] or flags["-t"] or flags["-a"]:
            sys.exit()

        # INTERPRETER PHASE--------------
        if flags["-i"]:
            pro_env = Environment(pro_scope)
            iv = InterpretVisitor(pro_env)
            if tree_node is not None:
                tree_node.accept(iv)
            sys.exit()

        # CODE GENERATION PHASE--------------
        if flags["-x"]:
            gev = XGenerateVisitor(pro_scope)
        else:
            gev = GenerateVisitor(pro_scope)
 
        if tree_node is not None:
            tree_node.accept(gev)
        
        if flags["file"]:
            # some assumptions made about the entered filename
            filename = sys.argv[len(sys.argv) - 1]
            splitlist = filename.split(".")
            basename = splitlist[0]
            newname = basename + ".s"

            f = open(newname, 'w')
            f.write(gev.output())
        else:
            print gev.output


    except CustException as err:
        if flags["-s"] and scan_start:
            print ''
            for tok in part_toks:
                print tok.to_string()

        sys.stderr.write("error: " + str(err) + '\n')


def usage(flags):
    if len(sys.argv) < 1 or len(sys.argv) > 4:  # check number of args
        raise CustException("Use './sc -<flag(s)> <optional filename>'")

    if len(sys.argv) > 1:  # check first flag
        if (sys.argv[1] != "-g" and sys.argv[1] != "file"
            and sys.argv[1] in flags):

            flags[sys.argv[1]] = True
        elif sys.argv[1] != "-g":
            flags["file"] = True
        else:
            raise CustException("Use './sc -<flag(s)> <optional filename>'")

    if len(sys.argv) > 2:  # check -g flag or filename
        if flags["file"]:
            raise CustException("Use './sc -<flag(s)> <optional filename>'")
        if sys.argv[2] == "-g":
            if not flags["-c"] and not flags["-t"] and not flags["-a"]:
                raise CustException("-g can only be used with -c,-t,or -a")
            else:
                flags["-g"] = True
        else:
            flags["file"] = True

    if len(sys.argv) > 3:  # check third argument (filename)
        if not flags["-g"]:  # only way we can have 3 args
            raise CustException("Use './sc -<flag(s)> <optional filename>'")
        else:
            flags["file"] = True


def get_source(flags):
    if flags["file"]:
        try:
            filename = sys.argv[len(sys.argv) - 1]
            infile = open(filename)
        except IOError:  # only cathcing to change name and message
            raise CustException("File " + filename + " not Found")
    else:
        infile = sys.stdin

    return infile.read()


main()
