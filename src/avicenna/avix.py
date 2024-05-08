# refine the import statements so they dont just import everything
import importlib
import os
from typing import Callable

from sflkit import *

from avicenna import Avicenna
from avicenna.oracle_construction import *


# maybe add oracle construction to avix separately as well to differentiate my contributions?
# add event files folder before init? 
class AviX(Avicenna):
    def __init__(
        self,
        desired_line: int,
        call_function: Callable,
        put_path: str,
        instr_path: str = 'rsc/instr.py',
        ):
        super().__init__()
        
        # requires the path to PUT and the instrumented version of it. save tmp.py in the folder for now, delete when done
        instrument(put_path=put_path, instr_path=instr_path)
        
        # importing instrumented function
        from avicenna.rsc import instr
        importlib.reload(instr)
        instr.sflkitlib.lib.reset()  
        
        self.oracle = construct_oracle(
            program_under_test=instr.middle, # TODO : make the function name dynamic somehow
            call_function=call_function,
            timeout=10,
            line=desired_line,
        ) # will be the line-Oracle, needs line and callable func and instrumentation
        
        
    def run_instr(call_function, instr_file_function, inp):
        call_function(instr_file_function, inp)
        


    """
        Create event-file for a given instrumented file and its input
    """
    def create_event_file(
            instr_func,
            inp, # string in
            conversion_func, # convert the inp string to an input usable by the function
            path, # used to call the instrumented version of a function (needed bcs funcs have different amounts/types of variables needed for calls)
        ): 
        # path must be a variable
        # os.environ['EVENTS_PATH'] = os.path.join('src/avicenna/rsc', '0') 
        # # make sure that event-file is actually written in the rsc folder
        os.environ['EVENTS_PATH'] = path
        
        from avicenna.rsc import instr  # TODO what is better style for this?
        importlib.reload(instr)
        instr.sflkitlib.lib.reset() # <-- this writes the event files
        
        converted_inp = conversion_func(inp) # must always return a list!!
        
        try:
            return instr_func(*converted_inp)
        finally:
            instr.sflkitlib.lib.dump_events()
            del instr
            
            
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

    # instrumentation call
    def instrument_avix(instr_path, put_path):
        return instrument_config(AviX.get_config(put_path=put_path, instr_path=instr_path))

    def import_instrumented():
        import avicenna.tmp
        importlib.reload(avicenna.tmp)
        avicenna.tmp.sflkitlib.lib.reset()
        return