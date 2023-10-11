from typing import Callable, Dict, Type, Optional
from pathlib import Path
import signal
from avicenna.oracle import OracleResult
from avicenna.input import Input


class ManageTimeout:
    def __init__(self, timeout: int):
        self.timeout = timeout

    def __enter__(self):
        set_alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        cancel_alarm()

# for managing event files below
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
    program_under_test: Callable,
    program_oracle: Optional[Callable],
    inp_converter: Optional[Callable] = None,
    error_definitions: Optional[Dict[Type[Exception], OracleResult]] = None,
    timeout: int = 1,
    default_oracle_result: OracleResult = OracleResult.UNDEF,
    line: int = None,
) -> Callable[[Input], OracleResult]:
    error_definitions = error_definitions or {}
    default_oracle_result = (
        OracleResult.BUG if not error_definitions else default_oracle_result
    )

    if not isinstance(error_definitions, dict):
        raise ValueError(f"Invalid value for expected_error: {error_definitions}")

    # Choose oracle construction method based on presence of program_oracle
    # TODO : refactor to switch case
    if program_oracle:
            oracle_constructor = _construct_functional_oracle
    elif line: 
        oracle_constructor = _construct_functional_line_oracle
        # added separate return here since line oracles need greatly different inputs
        return oracle_constructor(
            program_under_test,
            inp_converter,
            timeout,
            line,
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
def _construct_functional_line_oracle(
    program_under_test: Callable,
    inp_converter: Callable, # transforms the string input given by our grammar to be usable by the program under test (PUT)
    timeout: int,
    desired_line: int,
):
    def oracle(inp: Input) -> OracleResult:        
        # TODO : add call function 
        # ** ADD HERE **
        converted_inp = inp_converter(str(inp)) # list containing the PUT's inputs in order of the PUT's inputs
        
        try:
            # checks timeout exception and whether the line was triggered
            with ManageTimeout(timeout):
                program_under_test(converted_inp)

        except Exception as e:
            print(e) # exception was triggered, print for later use, maybe add to return somehow? global var?
            
        # ** add proper handling of created directories and files ** 
        path = Path('./resources/event_file') # This are the only file/folder that will exist and be deleted during each run
        
        with EventFile(path) as event_file:
            for line in event_file.readlines():
                cur_line = line.split(',')
                if cur_line[-2] == desired_line.str():
                    return OracleResult.BUG
                
            return OracleResult.NO_BUG

    return oracle


# running the instrumented PUT
# instrumentation happens in the beginning of AviX's run, the instrmented code is used here
def _run_instrumented_PUT(
    instr_PUT: Callable, # callable tmp PUT
    converted_inp: list, # list of inputs for PUT
    ):
    return instr_PUT(converted_inp)


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
        param = list(map(int, str(inp).strip().split()))  # This might become a problem
        try:
            # checks timeout exception
            with ManageTimeout(timeout):
                produced_result = program_under_test(*param)

            
            expected_result = program_oracle(*param)
            if expected_result != produced_result:
                raise UnexpectedResultError("Results do not match")
            
        except Exception as e:
            return error_definitions.get(type(e), default_oracle_result)
        return OracleResult.NO_BUG

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
        
        return OracleResult.NO_BUG

    return oracle
