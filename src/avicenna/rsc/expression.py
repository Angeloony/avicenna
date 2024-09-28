from typing import List

class Term:
    def evaluate(self) -> float | int:
        pass


class Binary(Term):
    def __init__(self, left: Term, right: Term):
        self.left = left
        self.right = right


class Add(Binary):
    def evaluate(self):
        l, r = self.left.evaluate(), self.right.evaluate()
        return l + r


class Sub(Binary):
    def evaluate(self):
        l, r = self.left.evaluate(), self.right.evaluate()
        return l - r


class Mul(Binary):
    def evaluate(self):
        l, r = self.left.evaluate(), self.right.evaluate()
        return l * r


class Div(Binary):
    def evaluate(self):
        l, r = self.left.evaluate(), self.right.evaluate()
        return l / r


class Neg(Term):
    def __init__(self, term: Term):
        self.term = term

    def evaluate(self) -> float | int:
        t = self.term.evaluate()
        return -t


class Constant(Term):
    def __init__(self, value: int):
        self.value = value

    def evaluate(self) -> float | int:
        return self.value


def parse(s: str):
    s = s.replace("(", " ( ")
    s = s.replace(")", " ) ")
    while "  " in s:
        s = s.replace("  ", " ")
    s = s.strip()
    tokens = list(reversed(s.split(" ")))
    assert tokens
    term = parse_add_sub(tokens)
    assert not tokens
    return term


def parse_terminal(tokens) -> Term:
    token = tokens.pop(0)
    if token.isnumeric():
        return Constant(int(token))
    elif token == ")":
        term = parse_add_sub(tokens) # reduce down to 1 line -> zsmfassen
        token = tokens.pop(0)
        assert token == "("
        return term
    else:
        assert False


def parse_neg(tokens) -> Term:
    term = parse_terminal(tokens)
    if tokens and tokens[0] in "~":
        tokens.pop(0)
        return Neg(term)
    else:
        return term


def parse_mul_div(tokens: List[str]) -> Term:
    term = parse_neg(tokens)
    if tokens and tokens[0] in "*/": #disjunction would be needed
        token = tokens.pop(0)
        if token == "*":
            return Mul(parse_mul_div(tokens), term)
        else:
            return Div(parse_mul_div(tokens), term)
    else:
        return term


def parse_add_sub(tokens: List[str]) -> Term:
    term = parse_mul_div(tokens)
    if tokens and tokens[0] in "+-":
        token = tokens.pop(0)
        if token == "+":
            return Add(parse_add_sub(tokens), term)
        else:
            return Sub(parse_add_sub(tokens), term)
    else:
        return term