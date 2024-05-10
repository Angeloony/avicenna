import string
import unittest
from pathlib import Path

from fuzzingbook.Grammars import Grammar

from avicenna.oracle_construction import (Input, OracleResult,
                                          UnexpectedResultError,
                                          _construct_line_oracle,
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
        self.resource_path = Path('tests/rsc/')


    # Check if path exists where we want it
    def test_path_exists(self):
        self.assertEqual(True, Path.exists(self.resource_path))
        
        
    # Check if middle inp converter works
    def test_middle_inp_converter(self):
        input = '1, 2, 3'
        self.assertEqual(middle_inp_conv(input), [1,2,3])
        
        
    # Whenever desired line is hit
    def test_line_hit(self):
        #from tests.rsc.instrumented import middle
        input = "2, 1, 3"
        line_oracle = construct_oracle(program_oracle=None,
                                       program_under_test='middle',
                                       inp_converter=middle_inp_conv,
                                       timeout=10,
                                       line=7,
                                       resource_path='tests/rsc/')
        
        self.assertEqual(
            line_oracle(input),
            OracleResult.FAILING
            )
    
    
    # Whenever desired line is missed
    def test_line_miss(self):
        #from tests.rsc.instrumented import middle
        input = "2, 1, 3"
        line_oracle = construct_oracle( program_oracle=None,
                                        program_under_test='middle',
                                        inp_converter=middle_inp_conv,
                                        timeout=10,
                                        line=5,
                                        resource_path='tests/rsc/'
                                        )
                
        self.assertEqual(
            OracleResult.PASSING,
            line_oracle(input)
            )


    # check if event files are created properly
    def test_multiple_inputs(self):
        #from .rsc.instrumented import middle 
        inputs =[
            "2, 1, 3", 
            "3, 2, 1", 
            "1, 2, 3"
            ]
        line_oracle = construct_oracle( program_oracle=None,
                                        program_under_test='middle',
                                        inp_converter=middle_inp_conv,
                                        timeout=10,
                                        line=7,
                                        resource_path='tests/rsc/')
        
        self.assertEqual(
            OracleResult.FAILING,
            line_oracle(inputs[0])
        )
        
        self.assertEqual(
            OracleResult.PASSING,
            line_oracle(inputs[2])
        )
        
        self.assertEqual(
            OracleResult.PASSING,
            line_oracle(inputs[1])
        )
        