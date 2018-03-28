# Graham Smith gsmth98@jhu.edu

from customexception import CustException
from token import Token


class Scanner:
    # language specifics
    __keywords = ['PROGRAM', 'BEGIN', 'END', 'CONST', 'TYPE',
        'VAR', 'ARRAY', 'OF', 'RECORD', 'DIV', 'MOD', 'IF',
        'THEN', 'ELSE', 'REPEAT', 'UNTIL', 'WHILE', 'DO',
        'WRITE', 'READ', 'PROCEDURE', 'RETURN']
    __symbols = [';', '.', '=', ':', '+', '-', '*', '(', ')',
        ':=', '#', '<', '>', '<=', '>=', '[', ']', ',']
    __whitespace = [' ', '\t', '\n', '\f', '\r']  # and comments

    def __init__(self, text):
        self.__pos = 0
        self.__source = text
        self.__next_called = False
        self.__eof = False

    def __white(self, char):
        return char in self.__whitespace

    def __key(self, word):
        return word in self.__keywords

    def __symbol(self, word):
        return word in self.__symbols

    def __letter(self, char):
        return (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z')

    def __digit(self, char):
        return char >= '0' and char <= '9'

    def next(self):
        self.__next_called = True
        while True:
            working = ''
            if self.__pos >= len(self.__source):
                self.__eof = True
                return Token('eof', self.__pos)
            curr = self.__source[self.__pos]

            # whitespace case -----------------------------------------
            if self.__white(curr):
                self.__pos += 1
                continue

            # letter case ----------------------------------------------
            elif self.__letter(curr):
                start_pos = self.__pos
                while self.__letter(curr) or self.__digit(curr):
                    working += curr
                    self.__pos += 1
                    if self.__pos >= len(self.__source):  # if I reach end
                        break
                    curr = self.__source[self.__pos]
                if self.__key(working):
                    return Token(working, start_pos)
                else:
                    return Token('identifier', start_pos, working)

            # digit case -----------------------------------------------
            elif self.__digit(curr):
                start_pos = self.__pos
                while self.__digit(curr):
                    working += curr
                    self.__pos += 1
                    if self.__pos >= len(self.__source):  # if I reach end
                        break
                    curr = self.__source[self.__pos]
                return Token('integer', start_pos, working)

            # symbol case ----------------------------------------------
            elif self.__symbol(curr):
                start_pos = self.__pos
                working += curr
                self.__pos += 1
                if self.__pos >= len(self.__source):  # if I reached end
                    return Token(working, start_pos)

                curr = self.__source[self.__pos]

                # check for 2-char symbol
                if self.__symbol(working + curr):
                    working += curr
                    self.__pos += 1

                # check for comment '(*'
                elif (working + curr) == '(*':
                    # pos/curr curently on the open *
                    # move it so we dont mistake '(*)' for a valid comment
                    self.__pos += 1
                    close = self.__source.find('*)', self.__pos)
                    if close == -1:
                        raise CustException('Unclosed comment starting at '
                            + str(start_pos))
                    self.__pos = close + 2  # the char after ) is close +2
                    continue

                return Token(working, start_pos)

            # Invalid case ---------------------------------------------
            else:
                raise CustException("Invalid character " + curr
                    + " at position " + str(self.__pos))

    def all(self, tok_list):
        if self.__next_called:
            raise CustException(
                "Cannot call all() after next() has been called")

        while not self.__eof:
            tok_list.append(self.next())
        return tok_list
