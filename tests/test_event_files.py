import unittest
from pathlib import Path
import string

from avicenna.oracle_construction import (
    construct_oracle,
    _construct_functional_line_oracle,
    OracleResult,
    Input,
    UnexpectedResultError,
)
from avicenna.avix import AviX
from fuzzingbook.Grammars import Grammar

grammar: Grammar = {
    "<start>": ["<input>"],
    "<input>": ["<first> <second>"],
    "<first>": ["<integer>"],
    "<second>": ["<integer>"],
    "<integer>": ["<one_nine><maybe_digits>"],  # no 0 at the moment
    "<one_nine>": [str(num) for num in range(1, 10)],
    "<digit>": list(string.digits),
    "<maybe_digits>": ["", "<digits>"],
    "<digits>": ["<digit>", "<digit><digits>"],
}

class TestEventFileConstructor(unittest.TestCase):
    def setUp(self):
        def conversion_middle(inp):
            inp = inp.__str__()
            middle_input = inp.split(',')
            # assume: conversion was successful. this func is passed when calling avix, so it has to be correct and deliver a result in a list
            converted_inp = [
                int(middle_input[0]),
                int(middle_input[1]),
                int(middle_input[2])
            ]
            return converted_inp
        
        inputs = [
            "3, 2, 1",
            "1, 2, 3",
            "2, 1, 3",
            "2, 3, 1"
        ]
        self.inp_converter = conversion_middle
        self.program_under_test = Path('./resources/instr.py')

    # first test, just try something and then see if it works lol
    def test_meow(self):
        from rsc import instr
        input = "2, 1, 3"
        converted = self.inp_converter(inp=input)
        AviX.create_event_file(instr_func=instr.middle,
                               inp=input, 
                               conversion_func=self.inp_converter)
        self.assertEqual(1,1)
# class TestConstructOracle(unittest.TestCase):
#     def setUp(self):
#         self.error_definitions = {
#             UnexpectedResultError: OracleResult.BUG,
#             TimeoutError: OracleResult.UNDEF,
#         }

#     def test_same_result(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             return x + y

#         my_oracle = construct_oracle(under_test, oracle, self.error_definitions)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.NO_BUG)

#     def test_different_result(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             return x - y

#         my_oracle = construct_oracle(under_test, oracle, self.error_definitions)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.BUG)

#     def test_defined_exception(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             raise TimeoutError()

#         my_oracle = construct_oracle(oracle, under_test, self.error_definitions)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.UNDEF)

#     def test_undefined_exception(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             raise ValueError()

#         my_oracle = construct_oracle(oracle, under_test, self.error_definitions)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.UNDEF)

#     def test_timeout_sleep(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             import time
#             time.sleep(2)
#             return x + y

#         my_oracle = construct_oracle(under_test, oracle, {UnexpectedResultError: OracleResult.NO_BUG, TimeoutError: OracleResult.BUG}, timeout=1)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.BUG)

#     def test_no_error_definition(self):
#         def oracle(x, y):
#             return x + y

#         def under_test(x, y):
#             raise ValueError

#         def under_test_unexpected_result_error(x, y):
#             raise x + y + 1

#         def under_test_timeout(x, y):
#             import time

#             time.sleep(2)
#             return x + y

#         my_oracle = construct_oracle(under_test, oracle)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.BUG)
#         my_oracle = construct_oracle(under_test_unexpected_result_error, oracle)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.BUG)
#         my_oracle = construct_oracle(under_test_timeout, oracle)
#         self.assertEqual(my_oracle(Input.from_str(grammar, "1 1")), OracleResult.BUG)


# if __name__ == "__main__":
#     unittest.main()
