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
            
        subject_attributes = {
            "name"      : "middle",
            "grammar"   : grammar_middle,
            "inputs"    : inputs_middle,
            "converter" : converter_middle,
            "lines"     : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
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
                #"-0",
                "0"
            ],
            "<maybe_minus>": [
                "",
                "-"
            ],
            "<maybe_frac>": ["", ".<digits>"],
            "<one_nine>": [str(num) for num in range(1, 10)],
            "<digit>": [digit for digit in string.digits],
            "<maybe_digits>": ["", "<digits>"],
            "<digits>": ["<digit>", "<digit><digits>"],
        } 

        inputs_calc = [
            'sqrt(9)', 'sqrt(-1)', 'sqrt(0)',
            'cos(8)', 'cos(-110)', 'cos(0)',
            'sin(8)', 'sin(-7)', 'sin(0)',
            'tan(8)', 'tan(-10)', 'tan(0)',
        ]
        
        subject_attributes = {
            "name"      : "calculator",
            "grammar"   : grammar_calc,
            "inputs"    : inputs_calc,
            "converter" : None,
            "lines"     : [
                1, 4, #import and empty line
                6, 8, 9, 10, 12, 13, 15, 16, #sqrt
                19, 20, #tan
                23, 24, #cos
                27, 28, #sin
                31, 32 #main
            ],
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
                1, 2, 6, 
                7,
                8, 
                9, 
                10, 
                11, 12, 
                13, 
                14,
                16
            ],
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
                "(<arith_expr>)",
            ],
            "<operator>": [" + ", " - ", " * ", " / "],
            "<number>": ["<maybe_minus><non_zero_digit><maybe_digits>", "0"],
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
                #1, 2, # import and empty line
                #3, 4, 5, #term
                #8, 9, 
                #10, #binary
                14, 16, #add
                #20, 21, 22, 23, #sub
                #26, 27, 28, 29, #mul
                #32, 33, 34, 35, #div
                #38, 39, 40, 41, 42, 43, 44, #neg
                #47, 48, 49, 51, 52, # Constant
                #55, 56, 59, 63, 64, 65, #parse func
                #68, 69, 71, 72, 73, 77, 78, # parse_terminal func, left out same branch lines
                #81, 82, 83, 85, 86, 87, #parse_neg func
                #90, 91, 92, 93, 94, 95, 96, 97, 98, 99, #parse_mul_div
                #102, 103, 104, 106, 107, 108, 109, 110, 111 #parse_add_sub
            ],
            "first_func": "parse", 
            "put_path"  : str(get_avicenna_rsc_path()) + '/' + "expression.py",
        } 
        
        return subject_attributes
    