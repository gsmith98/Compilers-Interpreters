# Graham Smith gsmith98@jhu.edu


class Entry(object):
    def accept(self, visitor):
        return visitor.visit(self)

    def to_string(self):
        return "Entry"


class Constant(Entry):
    def __init__(self, typ, val):
        self.__type = typ  # 'pointer' to type object
        self.__value = val  # just an integer (or whatever else)

    def getType(self):
        return self.__type

    def getValue(self):
        return self.__value

    def to_string(self):
        return "Constant " + self.__type.to_string() + " " + str(self.__value)

    def set_address(self, offset):
        self._address = offset

    def get_address(self):
        return self._address

class Variable(Entry):
    def __init__(self, typ):
        self.__type = typ  # 'pointer' to type object

    def getType(self):
        return self.__type

    def to_string(self):
        return "Variable " + self.__type.to_string()

    def set_address(self, offset):
        self._address = offset  # stored as offset from Variables label

    def get_address(self):
        return self._address


class Type(Entry):
    def to_string(self):
        return "Type"


class Procedure(Entry):
    def __init__(self, pms, scop, instrs):
        self.__params = pms
        self.__scope = scop
        self.__instructions = instrs

    def get_scope(self):
        return self.__scope

    def give_scope(self, scop):
        self.__scope = scop

    def get_instructions(self):
        return self.__instructions

    def give_instructions(self, instrs):
        self.__instructions = instrs

    def get_params(self):
        return self.__params


class Function(Entry):
    def __init__(self, pms, scop, instrs, exp, ret_typ):
        self.__params = pms
        self.__scope = scop
        self.__instructions = instrs
        self.__return = exp
        self.__return_type = ret_typ

    def get_scope(self):
        return self.__scope

    def give_scope(self, scop):
        self.__scope = scop

    def get_instructions(self):
        return self.__instructions

    def give_instructions(self, instrs):
        self.__instructions = instrs

    def get_return(self):
        return self.__return

    def give_return(self, exp):
        self.__return = exp

    def get_params(self):
        return self.__params

    def get_type(self):
        return self.__return_type


#http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern
class Integer(Type):
    __instance = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = Type.__new__(cls)
        return cls.__instance

    def to_string(self):
        return "Integer"

    def get_size(self):
        return 4


class Array(Type):
    def __init__(self, typ, leng):
        self.__elemtype = typ  # 'pointer' to type object
        self.__length = leng  # just an integer
        # I think not using a const object here is better
        # b/c const may later include booleans, etc

    def getType(self):
        return self.__elemtype

    def getLength(self):
        return self.__length

    def to_string(self):
        return ("Array " + self.__elemtype.to_string() + " "
            + str(self.__length))

    def get_size(self):
        return self.__length * self.__elemtype.get_size()


class Record(Type):
    def __init__(self, scop):
        self.__scope = scop  # 'pointer' to scope object

    def getScope(self):
        return self.__scope

    def to_string(self):
        return "Record with" + self.__scope.to_string()

    def get_size(self):
        return self.__scope.get_size()


# test singleton
if __name__ == "__main__":
    s1 = Integer()
    s2 = Integer()
    print id(s1)
    print id(s2)
