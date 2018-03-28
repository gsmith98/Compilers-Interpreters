# Graham Smith gsmith98@jhu.edu
from customexception import CustException


class Token:

    def __init__(self, text, position, meaning=''):
        # Token('blah') or Token('integer', '456')

        self.kind = text
        self.start_position = position

        if text == 'identifier':
            self.value = meaning
            self.end_position = position + len(meaning) - 1
        elif text == 'integer':
            self.value = int(meaning)
            self.end_position = position + len(meaning) - 1
        elif meaning != '':
            raise CustException("internal token constructor miscalled")
        elif text == 'eof':
            self.end_position = self.start_position
        else:
            self.end_position = position + len(text) - 1

    def to_string(self):
        s = self.kind

        if self.kind == 'identifier' or self.kind == 'integer':
            s += "<" + str(self.value) + ">"

        s += ("@(" + str(self.start_position) + ", "
            + str(self.end_position) + ")")
        return s
