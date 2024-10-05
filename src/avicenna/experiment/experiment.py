import logging
import time
import string
from pathlib import Path
from typing import Dict, Iterable, List, Callable

from avicenna.avix_help import get_avicenna_rsc_path

from tests4py.grammars.fuzzer import (
    srange,
)
from debugging_benchmark.tests4py_benchmark.grammars import grammar_markup

class Subject:
    def __init__(
        self,
        subject: Dict 
    ):
        self.name = subject["name"]
        self.grammar = subject["grammar"]
        self.inputs = subject["inputs"]
        self.converter = subject["converter"]
        self.relevant_lines = subject["lines"]
        self.first_func = subject["first_func"]
        self.put_path = subject["put_path"]
        self.results = None # will be replaced later
        
        
    def print_attributes(self):
        print("grammar: ")
        print(self.grammar)
        print("inputs: ")
        print(self.inputs)
        print("converter: ")
        print(self.converter)
    
    
    """ Subject getters """
    
    def get_middle():
        
        grammar_middle = {
            "<start>": ["<stmt>"],
            "<stmt>": ["<x>,<y>,<z>"],
            "<x>": ["<integer>"],
            "<y>": ["<integer>"],
            "<z>": ["<integer>"],
            "<integer>": ["<digit>", "<digit><integer>"],
            "<digit>": [str(num) for num in range(1, 10)]
        }
        
        inputs_middle = [
            '1,2,3', '2,1,3', '3,1,2',
            '2,3,1', '3,2,1', '1,3,2',           
        ]

        def converter_middle(inp):
            inp = inp.__str__()
            middle_input = inp.split(',')
            
            converted_inp = [
                int(middle_input[0]),
                int(middle_input[1]),
                int(middle_input[2])
            ]
            
            return converted_inp
        
        # TODO : producer stuff for all lines
        subject_attributes = {
            "name"      : "middle",
            "grammar"   : grammar_middle,
            "inputs"    : inputs_middle,
            "converter" : converter_middle,
            "lines"     : [
                #1, 2, 3,
                # 4, # 
                # #5, # ['1', '4']
                # #6, # ['1', '2']
                # #7, # ['1', '3', '4'] diff constraints check if they differ after tests maybe
                # # #8, 
                # 9, 
                # 10, 
                # 11, 
                # 12, 
                #13
            ], # 7 lines with analysis, 7 lines with returned constraints
            "first_func": "middle",
            "put_path"  : str(get_avicenna_rsc_path()) + '/' + "middle.py",
        } 
        
        return subject_attributes
    
    
    def get_calculator():
        
        grammar_calc = {
            "<start>": ["<arith_expr>"],
            "<arith_expr>": ["<function>(<number>)"],
            "<function>": ["sqrt", "sin", "cos", "tan"],
            "<number>": [
                "<maybe_minus><one_nine><maybe_digits><maybe_frac>",
                "<zero>"
            ],
            "<maybe_minus>": [
                "",
                "-"
            ],
            "<maybe_frac>": ["", ".<digits>"],
            "<maybe_digits>": ["", "<digits>"],
            "<digits>": [
                "<digit>",
                "<digit><digits>"
            ],
            "<zero>":["0"],
            "<one_nine>": [str(num) for num in range(1, 10)],
            "<digit>": [digit for digit in string.digits],
        } 

        inputs_calc = [
            'sqrt(9)', 'sqrt(-1)', 'sqrt(0)',
            'cos(8)', 'cos(-110)', 'cos(0)',
            'sin(8)', 'sin(-7)', 'sin(0)',
            'tan(8)', 'tan(-10)', 'tan(0)',
        ]
        
        # TODO : Producer stuff for all files
        subject_attributes = {
            "name"      : "calculator",
            "grammar"   : grammar_calc,
            "inputs"    : inputs_calc,
            "converter" : None,
            "lines"     : [
                # 1, 4, 32 are irrelevant for predict, no constraints
                #1, 4, #import and empty line
                #6,
                #8,  # ['1', '2', '3'] || 0 vs 1, 4, 5, 7 vs 2, 3, 6, 8, 9
                #9,  # ['1', '2']      || 0, 2, 3, 5, 7, 9, 10 vs 1, 4, 6
                #12, # ['3', '4', '1'] || 3 vs 4 vs rest
                #15, # ['1', '2']      || 1, 7 vs 2, 3, 4, 5, 6, 8, 9 no constraint on 10
                20, # ['1']           || all same 
                #24, # ['1', '10']     || 10 vs rest
                28, # ['1']           || all same 
                #32, #main
            ], # 8 lines with analysis, 8 lines with returned constraints
            "first_func": "main",
            "put_path"  : str(get_avicenna_rsc_path()) + '/' + "calculator.py",
        } 
        
        return subject_attributes
    
    
    def get_markup():
     #TODO doublecheck this grammar, what does it rly do, rewrite if possible   
        
        grammar_markup = {
            "<start>": ["<structure>"],
            "<structure>": ["<string>", "<html><structure>", "<string><html><structure>"],
            "<html>": ["<open><structure><close>"],
            "<open>": ["<LPAR><string><RPAR>"],
            "<close>": ["<LPAR>/<string><RPAR>"],
            "<LPAR>": ["<"],
            "<RPAR>": [">"],
            "<string>": ["", "<str>"],
            "<str>": ["<chars>"],
            "<chars>": ["<char>", "<char><chars>"],
            "<char>": [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
                "h",
                "i",
                "j",
                "k",
                "l",
                "m",
                "n",
                "o",
                "p",
                "q",
                "r",
                "s",
                "t",
                "u",
                "v",
                "w",
                "x",
                "y",
                "z",
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "J",
                "K",
                "L",
                "M",
                "N",
                "O",
                "P",
                "Q",
                "R",
                "S",
                "T",
                "U",
                "V",
                "W",
                "X",
                "Y",
                "Z",
                "!",
                '"',
                "#",
                "$",
                "%",
                "&",
                "'",
                "(",
                ")",
                "*",
                "+",
                ",",
                "-",
                ".",
                "/",
                ":",
                ";",
                "=",
                "?",
                "@",
                "[",
                "\\",
                "]",
                "^",
                "_",
                "`",
                "{",
                "|",
                "}",
                "~",
                " ",
            ],
        }
         
        # no inputs possible to trigger lines 7, 9, and 11 with. 
        # quotes and < > are mutually exclusive. strings cannot contain <> in this grammar.
        inputs_markup = [
            '"abc"',"abc",  "'a'''''''", ' '
            '"<b>abc</b>"', "<b>abc</b>", 
            "<b>abc</b> meow", "meow <b>abc</b>", "meow <b>abc</b> meow",
            "<b></b>", '"<b></b>"',
            '<b><baba></i@_gj32}4~></b>', 
            '<"baba"></123"b3423"""a645a">', "<b>'baba'</b>",
        ]
        
        subject_attributes = {
            "name"      : "markup",
            "grammar"   : grammar_markup,
            "inputs"    : inputs_markup,
            "converter" : None,
            "lines"     : [
                # 1, 6, 12 don't have constraints, dont need to predict
                #1, 
                #6, 
                8, # attempts ['6', '1']  check 6 vs rest
                10, # all same
                12, # none found
                14, # attempts ['9'], constraint vs no constraints
            ], # 4 lines with actual analysis, 3 with constraints
            "first_func": "remove_html_markup",
            "put_path"  : str(get_avicenna_rsc_path()) + '/' + "markup.py",
        } 
        
        return subject_attributes
  
    
    def get_expression():
        # TODO add new grammer with separate derivation for parentheses -> compare the two
        
        grammar_expression = {
            "<start>": ["<arith_expr>"],
            "<arith_expr>": [
                "<arith_expr><operator><arith_expr>",
                "<number>",
                "<par>",
            ],
            "<par>": ["<lpar><arith_expr><rpar>"],
            "<lpar>": ["("],
            "<rpar>": [")"],
            "<operator>": ["<plus>", "<minus>", "<mul>", "<div>"],
            "<plus>": [" + "],
            "<minus>": [" - "],
            "<mul>": [" * "],
            "<div>": [" / "],
            "<number>": [
                "<maybe_minus><non_zero_digit><maybe_digits>",
                "0"
            ],
            "<maybe_minus>": ["", "~ "],
            "<non_zero_digit>": [
                str(num) for num in range(1, 10)
            ],  # Exclude 0 from starting digits
            "<digit>": list(string.digits),
            "<maybe_digits>": ["", "<digits>"],
            "<digits>": ["<digit>", "<digit><digits>"],
        }
        
        # buggy behavior when divided by 0, otherwise try to trigger every possible function
        inputs_expression = [
            '5',    '(7)', '~ 8', # no space, doesn't trigger line 60
            '(9 - 5)', '16 - 5', '0 - (2 - 3)', '(7 - 2) - 3', # all -
            '(9 + 5)', '16 + 5', '0 + (2 + 3)', '(7 + 2) + 3', # all +
            '(9 * 5)', '16 * 5', '0 * (2 * 3)', '(7 * 2) * 3', # all *
            '(9 / 5)', '16 / 5', '0 / (2 / 3)', '(7 / 2) / 3', # all /
            '(9 / 5) * 2', '16 / 5 + 5', '0 / (2 / 3)', '(7 / 2) - 3', # mix operators
            '(7 + 2) * 3','(7 / 2) + 3', '7 - (2 / 3)',                # mix mult and add
            '(9 / 5) + 8', '16 / 5 - 5', '0 / (2 * 0)', '7 / 2 / 0',   # div by 0
            '9 + 8', # add ~ tilde for inputs
            '(~ 9 + 5)', '16 + ~ 5', '0 + (2 + 3)', '(7 + 2) + 3', # all +
            
        ]
        
        subject_attributes = {
            "name"      : "expression",
            "grammar"   : grammar_expression,
            "inputs"    : inputs_expression,
            "converter" : None,
            "lines"     : [
                # TODO : run lines 10, 87 overnight for constraints (87 prolly wont have)
                # TODO : predictor all lines
                # TODO : producer all lines
                # lines 49, 71, 86, 87, 99, 111, do not have constraints - no predict
                #10, # init Binary | at least 10 min  || check attempts
                40, # init Negate | at least 1 minute || all same
                #49, # init Constant DONE | instant   || no constraints
                59, # check for space | about 5 min at least || all same ['1']
                #71, # DONE checking isnumeric()  || no constraints
                73, # parenthesis check | about 5 min || all same 
                85, # return Negate Term | about 1 min || all same
                #86, # DONE instant i tihnk? || no constraint
                #87, # return parse_neg | about 1h long - no constraint || no constraint BUT RELEVANT cuz we still searched NOT RUN YET
                93, # go into mul_div | about 2 min to 5 min || all same, not found in attempt 7
                95, # return Mul | about 5 min different constraint results here || attempt 0, 2, 7, 8, 9 vs 1, 3, 4, 5, 6 | ['1', '2']
                97, # return Div | || all same
                #99, # return parsemuldiv | instant || no constraint
                105,# go into add_sub | about 5 min different constraint results here || attempts 1, 2, 4, 5, vs 3, vs 8, vs 9 vs 10 no constraint | ['1', '3', '8', '9'] IMPORTANT: NO CONSTRAINT FOUND ONCE 
                107,# return Add | about 5 min different constraint results here || 7, 10, vs rest of lines | ['1', '7']
                109,# return Sub | about 5 min different constraint results here || 0, 6 ,8 vs 1, 2, vs 3, 4, 5, 7, 9 | ['1', '2', '4']
                #111,# return parseaddsub | instant
            ],
            "first_func": "parse", 
            "put_path"  : str(get_avicenna_rsc_path()) + '/' + "expression.py",
        } 
        
        return subject_attributes
    