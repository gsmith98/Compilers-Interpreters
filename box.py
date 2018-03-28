# Graham Smith gsmith98@jhu.edu

from entry import *
import environment
from customexception import *


class Box(object):
    def __new__(cls, typ_entry):
        if isinstance(typ_entry, Integer):
            return object.__new__(IntegerBox, typ_entry)
        elif isinstance(typ_entry, Array):
            return object.__new__(ArrayBox, typ_entry)
        elif isinstance(typ_entry, Record):
            return object.__new__(RecordBox, typ_entry)
        else:
            raise CustException("Failed Box type sanity check")


class IntegerBox(Box):
    def __init__(self, typ_entry):
        self._int = 0

    def set_int(self, val):
        self._int = val

    def get_int(self):
        return self._int

    def assign(self, intbox2):
        self._int = intbox2.get_int()


class ArrayBox(Box):
    def __init__(self, arr_entry):
        self._boxes = []
        self._length = arr_entry.getLength()
        for num in range(self._length):
            self._boxes.append(Box(arr_entry.getType()))
            # makes list of length boxes for arr's elemtype

    def get_box(self, index):
        if index >= self._length:
            raise CustException("Index " + str(index)
                + " out of bounds. Array length " + str(self._length))

        return self._boxes[index]

    # can only be done if both are the exact same kind of arraybox
    def assign(self, arrbox2):
        for num in range(self._length):
            self._boxes[num].assign(arrbox2.get_box(num))


class RecordBox(Box):
    def __init__(self, rec_entry):
        self._env = environment.Environment(rec_entry.getScope())

    def get_box(self, field):
        return self._env.get_box(field)

    def assign(self, recbox2):
        boxes = self._env.get_boxes()
        for name in boxes:
            boxes[name].assign(recbox2.get_box(name))
