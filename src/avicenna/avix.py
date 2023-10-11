# refine the import statements so they dont just import everything
from avicenna import Avicenna
from avicenna.oracle_construction import *

from typing import Callable

from sflkit import * 
import importlib


# maybe add oracle construction to avix separately as well to differentiate my contributions?
# add event files folder before init? 
class AviX(Avicenna):
    def __init__(
        self,
        desired_line: int,
        call_function: Callable,
        put_path: str,
        instr_path: str = 'tmp.py',
        ):
        super().__init__()
        
        # requires the path to PUT and the instrumented version of it. save tmp.py in the folder for now, delete when done
        instrument(put_path=put_path, instr_path=instr_path)
        
        # importing instrumented function
        import avicenna.tmp
        importlib.reload(avicenna.tmp)
        avicenna.tmp.sflkitlib.lib.reset()  
        
        self.oracle = construct_oracle(
            program_under_test=avicenna.tmp.middle, # TODO : make the function name dynamic somehow
            call_function=call_function,
            timeout=10,
            line=desired_line,
        ) # will be the line-Oracle, needs line and callable func and instrumentation
        

# config for instrumentation, needs path for PUT and instrumentation, instr might be obsolete later
def get_config(
        put_path,
        instr_path,
    ):
    return Config.create(
        path=put_path, 
        working=instr_path, 
        language='python',
        predicates='line'
    )


def instrument(instr_put, put_path):
    instrument_config(get_config(put_path, instr_put)) 


def import_instrumented():
    import avicenna.tmp
    importlib.reload(avicenna.tmp)
    avicenna.tmp.sflkitlib.lib.reset()
    return