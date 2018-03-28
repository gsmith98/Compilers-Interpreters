# Graham Smith gsmith98@jhu.edu


from node import *
from scope import *


# intermediate representation object to hold both ST and AST
class IR(object):
    def __init__(self):
        self.st_scope = None
        self.ast_tree = None
