# Graham Smith gsmith98@jhu.edu

from customexception import CustException
from entry import *

class Scope(object):
    def __init__(self, out):
        self.__outer = out  # pointer to outer scope
        self.__table = {}  # dictionary: the symbol table

    def insert(self, name, entry):
        if name in self.__table:  # could call local, but I find this clearer
            raise CustException(name + " declared a second time in same scope")

        self.__table[name] = entry

    def find(self, name):
        if name in self.__table:
            return self.__table[name]
        elif self.__outer is not None:
            return self.__outer.find(name)
        else:
            return None

    def local(self, name):
        return name in self.__table

    def to_string(self):
        return "Scope " + str(self.__table)

    def sever(self):
        self.__outer = None

    def getTable(self):
        return self.__table

    def accept(self, visitor):
        return visitor.visit(self)

    def get_size(self):
        summ = 0
        for name in self.__table:
            ent = self.__table[name]
            if not isinstance(ent, Type):
                summ += ent.getType().get_size()
                if isinstance(ent, Constant) and (
                    ent.getValue() < -(2**31) or ent.getValue() > (2**31) - 1):
                    raise CustException("Value " + str(ent.getValue()) +
                        " won't fit in a 32 bit register")

        if summ > 2**16: # maximum offset tht can be used
            raise CustException("Space needed surpassed addressable bounds")
        return summ

    # give offset from the beginning of the containing scope
    # a record may be at offset 8, its first member at
    # offset 0 (from that 8)
    def give_offsets(self):
        off = 0
        for name in self.__table:
            if not isinstance(self.__table[name], Type):
                self.__table[name].set_address(off)
                if isinstance(self.__table[name].getType(), Record):
                    self.__table[name].getType().getScope().give_offsets()
                off += self.__table[name].getType().get_size()
