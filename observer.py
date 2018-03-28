# Graham Smith gsmith98@jhu.edu

from entry import *


class Observer:
    def notifyMatch(self, tok):
        pass

    def notifyStart(self, funcName):
        pass

    def notifyEnd(self):
        pass

    def output(self):
        pass


class textObserver(Observer):
    def __init__(self):
        self.__s = ""
        self.__indent = 0

    def notifyMatch(self, tok):
        for num in range(self.__indent):
            self.__s += " "
        self.__s += tok.to_string() + "\n"

    def notifyStart(self, funcName):
        for num in range(self.__indent):
            self.__s += " "
        self.__s += funcName[2:] + "\n"
        self.__indent += 2

    def notifyEnd(self):
        self.__indent -= 2

    def output(self):
        print self.__s


class graphicalObserver(Observer):
    def __init__(self):
        self.__s = ""
        self.__count = 0
        self.__stack = []

    def notifyMatch(self, tok):
        node = "L" + str(self.__count)
        self.__count += 1
        if tok.kind in ["identifier", "integer"]:
            name = str(tok.value)
        else:
            name = tok.kind

        self.__s += node + " [label=\"" + name + "\",shape=diamond]\n"
        if self.__stack:  # if not empty
            parent = self.__stack[len(self.__stack) - 1]
            self.__s += parent + " -> " + node + "\n"

    def notifyStart(self, funcName):
        node = "L" + str(self.__count)
        self.__count += 1
        self.__s += node + " [label=\"" + funcName[2:] + "\",shape=box]\n"
        if self.__stack:  # if not empty
            parent = self.__stack[len(self.__stack) - 1]
            self.__s += parent + " -> " + node + "\n"

        self.__stack.append(node)

    def notifyEnd(self):
        self.__stack.pop()

    def output(self):
        print "strict digraph CST { \n" + self.__s + "}"
