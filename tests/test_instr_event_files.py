import filecmp
import os
import shutil
import string
import unittest

from pathlib import Path

from fuzzingbook.Grammars import Grammar
from sflkit import instrument

from avicenna.avix import AviX
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

class TestEventFileConstructor(unittest.TestCase):
    
    def setUp(self):
        
        def middle_converter(inp):
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
        
        self.inp_converter = middle_converter
        self.program_under_test = Path('tests/rsc/middle.py')
        self.instr_path = Path('tests/rsc/instrumented.py')
        self.tmp_path = Path('tests/tmp/')
        
        
    # Check for correct instrumentation
    def test_instrument(self):
        
        AviX.instrument_avix(put_path=str(self.program_under_test),
                             instr_path='tests/rsc/tmp.py')
        
        self.assertEqual(
            True,
            filecmp.cmp('tests/rsc/tmp.py', self.instr_path)
            )
    
    
    def test_path_exists(self):
        self.assertEqual(
            True,
            Path.exists(Path(self.instr_path))
        )
        
        self.assertEqual(
            True,
            Path.exists(Path(self.tmp_path))
        )
        
        self.assertEqual(
            True,
            Path.exists(Path(self.program_under_test))
        )
        

    # TODO : use a program with multiple files to test for this
    # This will be important in order to check how the instrumentation works.
    # How many files will be get back? Do we have to enter file names into line oracle? etc.
    #def test_instrument_mult_files(self):
    # Test creation of event_files
    def test_event_file_creation(self):
        
        # delete old event files first
        # if os.path.exists(self.tmp_path):
        #     shutil.rmtree(self.tmp_path)
        # os.mkdir(self.tmp_path)
        
        # create new event files
        #from tests.rsc.instrumented import middle
        
        self.assertEqual(
            True,
            Path.exists(Path(self.instr_path))
        )
        
        input = "2, 1, 3"
        event_path = os.path.join(str(self.tmp_path), 'event_file')
        AviX.create_event_file(instrumented_function='middle',
                               inp=input, 
                               conversion_func=self.inp_converter,
                               event_path= event_path,
        )
        
        self.assertEqual(
            True,
            Path.exists(Path(event_path))
        )