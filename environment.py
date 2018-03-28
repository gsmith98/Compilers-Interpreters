# Graham Smith gsmith98@jhu.edu

from customexception import *
from entry import *
from box import *


class Environment(object):
    def __init__(self, scope):
        self._boxes = {}
        tab = scope.getTable()
        for name in tab:
            if not isinstance(tab[name], Variable):
                continue

            typ_entry = tab[name].getType()
            self._boxes[name] = Box(typ_entry)

    def get_box(self, name):
        if name in self._boxes:
            return self._boxes[name]
        else:
            raise CustException("Environment has no box " + name)

    def get_boxes(self):
        return self._boxes
