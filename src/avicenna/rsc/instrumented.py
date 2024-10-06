import sflkitlib.lib
sflkitlib.lib.add_line_event(0)
from typing import List

class Term:

    def evaluate(self) -> float | int:
        sflkitlib.lib.add_line_event(1)
        pass

class Binary(Term):

    def __init__(self, left: Term, right: Term):
        sflkitlib.lib.add_line_event(2)
        self.left = left
        sflkitlib.lib.add_line_event(3)
        self.right = right

class Add(Binary):

    def evaluate(self):
        sflkitlib.lib.add_line_event(4)
        (l, r) = (self.left.evaluate(), self.right.evaluate())
        sflkitlib.lib.add_line_event(5)
        return l + r

class Sub(Binary):

    def evaluate(self):
        sflkitlib.lib.add_line_event(6)
        (l, r) = (self.left.evaluate(), self.right.evaluate())
        sflkitlib.lib.add_line_event(7)
        return l - r

class Mul(Binary):

    def evaluate(self):
        sflkitlib.lib.add_line_event(8)
        (l, r) = (self.left.evaluate(), self.right.evaluate())
        sflkitlib.lib.add_line_event(9)
        return l * r

class Div(Binary):

    def evaluate(self):
        sflkitlib.lib.add_line_event(10)
        (l, r) = (self.left.evaluate(), self.right.evaluate())
        sflkitlib.lib.add_line_event(11)
        return l / r

class Neg(Term):

    def __init__(self, term: Term):
        sflkitlib.lib.add_line_event(12)
        self.term = term

    def evaluate(self) -> float | int:
        sflkitlib.lib.add_line_event(13)
        t = self.term.evaluate()
        sflkitlib.lib.add_line_event(14)
        return -t

class Constant(Term):

    def __init__(self, value: int):
        sflkitlib.lib.add_line_event(15)
        self.value = value

    def evaluate(self) -> float | int:
        sflkitlib.lib.add_line_event(16)
        return self.value

def parse(s: str):
    sflkitlib.lib.add_line_event(17)
    s = s.replace('(', ' ( ')
    sflkitlib.lib.add_line_event(18)
    s = s.replace(')', ' ) ')
    sflkitlib.lib.add_line_event(19)
    while '  ' in s:
        sflkitlib.lib.add_line_event(20)
        s = s.replace('  ', ' ')
    sflkitlib.lib.add_line_event(21)
    s = s.strip()
    sflkitlib.lib.add_line_event(22)
    tokens = list(reversed(s.split(' ')))
    sflkitlib.lib.add_line_event(23)
    assert tokens
    sflkitlib.lib.add_line_event(24)
    term = parse_add_sub(tokens)
    sflkitlib.lib.add_line_event(25)
    assert not tokens
    sflkitlib.lib.add_line_event(26)
    return term

def parse_terminal(tokens) -> Term:
    sflkitlib.lib.add_line_event(27)
    token = tokens.pop(0)
    sflkitlib.lib.add_line_event(28)
    if token.isnumeric():
        sflkitlib.lib.add_line_event(29)
        return Constant(int(token))
    else:
        sflkitlib.lib.add_line_event(30)
        if token == ')':
            sflkitlib.lib.add_line_event(31)
            term = parse_add_sub(tokens)
            sflkitlib.lib.add_line_event(32)
            token = tokens.pop(0)
            sflkitlib.lib.add_line_event(33)
            assert token == '('
            sflkitlib.lib.add_line_event(34)
            return term
        else:
            sflkitlib.lib.add_line_event(35)
            assert False

def parse_neg(tokens) -> Term:
    sflkitlib.lib.add_line_event(36)
    term = parse_terminal(tokens)
    sflkitlib.lib.add_line_event(37)
    if tokens and tokens[0] in '~':
        sflkitlib.lib.add_line_event(38)
        tokens.pop(0)
        sflkitlib.lib.add_line_event(39)
        return Neg(term)
    else:
        sflkitlib.lib.add_line_event(40)
        return term

def parse_mul_div(tokens: List[str]) -> Term:
    sflkitlib.lib.add_line_event(41)
    term = parse_neg(tokens)
    sflkitlib.lib.add_line_event(42)
    if tokens and tokens[0] in '*/':
        sflkitlib.lib.add_line_event(43)
        token = tokens.pop(0)
        sflkitlib.lib.add_line_event(44)
        if token == '*':
            sflkitlib.lib.add_line_event(45)
            return Mul(parse_mul_div(tokens), term)
        else:
            sflkitlib.lib.add_line_event(46)
            return Div(parse_mul_div(tokens), term)
    else:
        sflkitlib.lib.add_line_event(47)
        return term

def parse_add_sub(tokens: List[str]) -> Term:
    sflkitlib.lib.add_line_event(48)
    term = parse_mul_div(tokens)
    sflkitlib.lib.add_line_event(49)
    if tokens and tokens[0] in '+-':
        sflkitlib.lib.add_line_event(50)
        token = tokens.pop(0)
        sflkitlib.lib.add_line_event(51)
        if token == '+':
            sflkitlib.lib.add_line_event(52)
            return Add(parse_add_sub(tokens), term)
        else:
            sflkitlib.lib.add_line_event(53)
            return Sub(parse_add_sub(tokens), term)
    else:
        sflkitlib.lib.add_line_event(54)
        return term