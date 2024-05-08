import string
import unittest
from pathlib import Path

from fuzzingbook.Grammars import Grammar

from avicenna.oracle_construction import (Input, OracleResult,
                                          UnexpectedResultError,
                                          _construct_functional_line_oracle,
                                          construct_oracle)

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

# converts string inputs to lists of ints
def middle_inp_conv(inp):
    inp = inp.__str__()
    middle_input = inp.split(',')
    
    converted_inp = [
        int(middle_input[0]),
        int(middle_input[1]),
        int(middle_input[2])
    ]
    
    return converted_inp

class TestConstructLineOracle(unittest.TestCase):
    def setUp(self):
        
        self.inp_converter = middle_inp_conv
        self.event_file_path = Path('tests/rsc/event_file')
        self.program_under_test = Path('tests/rsc/instr.py')

    # Check if path exists where we want it
    def test_path_exists(self):
        self.assertEqual(True, Path.exists(self.program_under_test))
        
    # Check if middle inp converter works
    def test_middle_inp_converter(self):
        input = '1, 2, 3'
        self.assertEqual(middle_inp_conv(input), [1,2,3])
        
    # Whenever desired line is hit
    def test_oracle_line_hit(self):
        from rsc.instr import middle
        input = "2, 1, 3"
        line_oracle = construct_oracle(program_oracle=None,
                                       program_under_test=middle,
                                       inp_converter=middle_inp_conv,
                                       timeout=10,
                                       line=6,
                                       event_file_path='tests/rsc/event_file')
        
        
        self.assertEqual(
            line_oracle(input),
            OracleResult.FAILING
            )
    
    # Whenever desired line is missed
    def test_oracle_line_miss(self):
        from rsc.instr import middle
        input = "2, 1, 3"
        line_oracle = construct_oracle( program_oracle=None,
                                        program_under_test=middle,
                                        inp_converter=middle_inp_conv,
                                        timeout=10,
                                        line=5,
                                        event_file_path='tests/rsc/event_file')
                
        self.assertEqual(
            OracleResult.PASSING,
            line_oracle(input)
            )
