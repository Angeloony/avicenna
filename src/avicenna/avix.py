# refine the import statements so they dont just import everything
import os

from typing import Callable, Dict, List, Optional, Type

from debugging_framework.input.oracle import OracleResult

from fuzzingbook.Grammars import Grammar

from sflkit.config import Config
from sflkit.analysis.spectra import Line

from avicenna import Avicenna
from avicenna.input import Input

from avicenna.avix_help import (analyzer_conf, get_avicenna_rsc_path,
                                import_instrumented, instrument)


# maybe add oracle construction to avix separately as well to differentiate my contributions?
# add event files folder before init? 
class AviX(Avicenna):
    
    
    def __init__(
        self,
        put_path: str,
        grammar: Grammar,
        oracle: Callable[[Input], OracleResult],
        initial_inputs: List[str],
        
        instr_path: str = str(get_avicenna_rsc_path()) + '/instrumented.py',
        max_iterations: int = 10,
        top_n_relevant_features: int = 3,
        ):
        
        # requires the path to PUT and the instrumented version of it. save tmp.py in the folder for now, delete when done
        instrument(put_path=put_path, instr_path=instr_path)
        
        # init avicenna class object
        super().__init__(
            grammar=grammar,
            oracle=oracle,
            initial_inputs=initial_inputs,
            max_iterations=max_iterations,
            top_n_relevant_features=top_n_relevant_features
        )


    # Running SFLKit analysis on lines triggered etc. in event files.
    # Returns list of integers.
    def run_sfl_analysis(conf: Config):

        analyzer = analyzer_conf(conf)
        
        analyzer.analyze()
        
        coverage: List[Line] = analyzer.get_coverage()
        coverage = {line.line for line in coverage}
        
        return coverage


    """
        Create event-file for a given instrumented file and its input
    """

    def create_event_file(
        inp: str,                   # string inputs which will have to be converted later on
        instrumented_function: str, # name of the function-under-test used for dynamic imports
        inp_converter: Optional[Callable] = None,  # used for conversion of inp
        
        event_path: str = str(get_avicenna_rsc_path()),   # path to event_files. Usually rsc/            
    ): 
        if inp_converter:
            converted_inp = inp_converter(inp) # must always return a list!!
        else:
            converted_inp = inp
        
        # delete old event files first
        if os.path.exists(event_path):
            os.unlink(event_path)
        # make sure that event-file is actually written in the rsc folder
        os.environ['EVENTS_PATH'] = event_path    
        
        # this ends up creating the event file
        import_instrumented(instrumented_function, converted_inp)

        