import importlib
import os
import signal
from pathlib import Path
from typing import Callable, Dict, Optional, Type, Union

from debugging_framework.input.oracle import OracleResult

from avicenna.avix import AviX
from avicenna.input import Input
from avicenna.avix_help import get_avicenna_rsc_path, get_sfl_config

class ManageTimeout:
    def __init__(self, timeout: int):
        self.timeout = timeout

    def __enter__(self):
        set_alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        cancel_alarm()

# for managing event files below (line oracle)
class EventFile:
    def __init__(self, file_name: str):
        self.file = open(file_name, newline='')
        
    def __enter__(self):
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        

class UnexpectedResultError(Exception):
    pass


# Define the handler to be called when the alarm signal is received
def alarm_handler(signum, frame):
    raise TimeoutError("Function call timed out")


# Set the alarm signal handler
signal.signal(signal.SIGALRM, alarm_handler)


def set_alarm(seconds: int):
    signal.alarm(seconds)


def cancel_alarm():
    signal.alarm(0)


def construct_oracle(
    program_under_test: Union[Callable, str], # name of the first function to enter im pretty sure
    program_oracle: Optional[Callable] = None,
    error_definitions: Optional[Dict[Type[Exception], OracleResult]] = None,
    timeout: int = 1,
    default_oracle_result: OracleResult = OracleResult.UNDEFINED,
    line: int = None,
    put_path = Optional[str],
    inp_converter: Optional[Callable] = None, # used for line oracle 
    resource_path: Optional[str] = str(get_avicenna_rsc_path()), #needed for line oracle, standard is the file path to src/avicenna/rsc
) -> Callable[[Input], OracleResult]:
    
    error_definitions = error_definitions or {}
    default_oracle_result = (
        OracleResult.FAILING if not error_definitions else default_oracle_result
    )

    if not isinstance(error_definitions, dict):
        raise ValueError(f"Invalid value for expected_error: {error_definitions}")

    # Choose oracle construction method based on presence of program_oracle
    # TODO : refactor to switch case
    if program_oracle:
            oracle_constructor = _construct_functional_oracle
    elif line: 
        oracle_constructor = _construct_line_oracle
        # added separate return here since line oracles need vastly different inputs
        return oracle_constructor(
            program_under_test=program_under_test,
            inp_converter=inp_converter,
            timeout=timeout,
            desired_line=line,
            resource_path=resource_path,
            put_path=put_path
        )
    else: 
        oracle_constructor = _construct_failure_oracle
    
    
    return oracle_constructor(
        program_under_test,
        program_oracle,
        error_definitions,
        timeout,
        default_oracle_result,
    )

# ** UNDER CONSTRUCTION **
# important: oracles will be hard coded before-hand and must maintain a given shape
def _construct_line_oracle(
    program_under_test: str, # name of function we want to run later TODO talk to martin if this makes sense
    desired_line: int,
    resource_path: str, # event files and instrumented files etc are here  
    put_path: str,    
    timeout: int,
    
    inp_converter: Optional[Callable] = None, # transforms the string input given by our grammar to be usable by the program under test (PUT)
):
    #instrumented_file_path = resource_path + 'instrumented.py' TODO check if i can dynamically do this
    event_file_path = resource_path + '/event_file'
    
    
    def oracle(inp: Input) -> OracleResult:     
        try:
            # checks timeout exception and whether the line was triggered
            with ManageTimeout(timeout):
                # run instrumented program and save event file here
                # TODO : check this function call, rename stuff 
                AviX.create_event_file( instrumented_function=program_under_test,
                                        #instr_path=instrumented_file_path,
                                        inp=str(inp), 
                                        inp_converter=inp_converter, 
                                        event_path=event_file_path,
                )            
        except Exception as e:
            print(e)
            return OracleResult.UNDEFINED # exception was triggered, print for later use, maybe add to return somehow? global var?
        
        # TODO : double check this call middle cant be right here
        coverage = AviX.run_sfl_analysis(
            get_sfl_config(
                failing=event_file_path, 
                put_path=put_path,#put_path, # path to the base file
                instr_path=resource_path + '/instrumented.py'
            ))
        #print(coverage)
        #print(desired_line)
        if desired_line in coverage:
            # print(coverage)
            return OracleResult.FAILING
        else: 
            # print(coverage)
            # print(inp)
            return OracleResult.PASSING  

    return oracle

# call this if an oracle was defined and given 
# this could check for our line to be called
def _construct_functional_oracle(
    program_under_test: Callable,
    program_oracle: Callable,
    error_definitions: Dict[Type[Exception], OracleResult],
    timeout: int,
    default_oracle_result: OracleResult,
):
    def oracle(inp: Input) -> OracleResult:
        # param list needs to be extended to account for the desired line to be called
        param = list(map(int, str(inp).strip().split(',')))  # This might become a problem
        try:
            # checks timeout exception
            with ManageTimeout(timeout):
                produced_result = program_under_test(*param)

            
            expected_result = program_oracle(*param)
            if expected_result != produced_result:
                raise UnexpectedResultError("Results do not match")
            
        except Exception as e:
            return error_definitions.get(type(e), default_oracle_result)
        return OracleResult.PASSING

    return oracle


# only works when a failure occurs, meaning the program under test must throw an exception
def _construct_failure_oracle(
    program_under_test: Callable,
    error_definitions: Dict[Type[Exception], OracleResult],
    timeout: int,
    default_oracle_result: OracleResult,
):
    def oracle(inp: Input) -> OracleResult:
        try:
            with ManageTimeout(timeout):
                program_under_test(str(inp))
                
        except Exception as e:
            return error_definitions.get(type(e), default_oracle_result)
        
        return OracleResult.PASSING

    return oracle
