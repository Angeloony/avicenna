# refine the import statements so they dont just import everything
import os

from typing import Callable, Dict, List, Optional, Type

from debugging_framework.input.oracle import OracleResult

from fuzzingbook.Grammars import Grammar

from sflkit import *
from sflkit.analysis import factory
from sflkit.analysis.spectra import Line

from avicenna import Avicenna
from avicenna.input import Input

from avicenna.avix_help import get_avicenna_rsc_path


# maybe add oracle construction to avix separately as well to differentiate my contributions?
# add event files folder before init? 
class AviX(Avicenna):
    
    
    def __init__(
        self,
        put_path: str,
        grammar: Grammar,
        oracle: Callable[[Input], OracleResult],
        initial_inputs: List[str],
        
        instr_path: str = str(get_avicenna_rsc_path()),
        max_iterations: int = 10,
        top_n_relevant_features: int = 3,
        ):
        
        # init avicenna class object
        super().__init__(
            grammar=grammar,
            oracle=oracle,
            initial_inputs=initial_inputs,
            max_iterations=max_iterations,
            top_n_relevant_features=top_n_relevant_features
        )
            
        # requires the path to PUT and the instrumented version of it. save tmp.py in the folder for now, delete when done
        AviX.instrument_avix(put_path=put_path, instr_path=instr_path)
      

    # Embedded SFLKit's instrumentation into AviX
    def instrument_avix(
        put_path:   str,
        instr_path: str,
    ):
        # taken from sflkit
        return instrument_config(AviX._get_config(put_path=put_path,
                                                  instr_path=instr_path)
                                 )


    
    # Running SFLKit analysis on lines triggered etc. in event files.
    # Returns list of integers.
    def run_sfl_analysis(
        failing=None,
        passing=None,
        put_path=None,
        instr_path=None
    ):

        analyzer = AviX.analyzer_conf(
            AviX._get_config(put_path=put_path,
                            instr_path=instr_path,
                            failing=failing,
                            passing=passing))
        
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
        conversion_func: Callable,  # used for conversion of inp
        
        event_path: str = 'rsc/',   # path to event_files. Usually rsc/            
    ): 
        if conversion_func != None:
            converted_inp = conversion_func(inp) # must always return a list!!
        else:
            converted_inp = inp
        
        # delete old event files first
        if os.path.exists(event_path):
            os.unlink(event_path)
        # make sure that event-file is actually written in the rsc folder
        os.environ['EVENTS_PATH'] = event_path    
        
        # this ends up creating the event file
        AviX.import_instrumented_module(instrumented_function, converted_inp)

          

    """ Instrumentation funcs and helper funcs"""
    
    # config for instrumentation, needs path for PUT and instrumentation, instr might be obsolete later
    def _get_config(          
        put_path:   str = None,
        instr_path: str = None,
        language:   str = 'python',
        predicates: str = 'line',
        passing:    str = None, 
        failing:    str = None,
    ):
        
        return Config.create(
            path=put_path, 
            working=instr_path, 
            language=language,
            predicates=predicates,
            failing=failing,
            passing=passing,
        )
        
    
    # Used to create an Analyzer object used by SFLKit for line-trigger analyses etc.
    def analyzer_conf(conf: Config):
        
        analyzer = Analyzer(irrelevant_event_files=conf.failing,
                            relevant_event_files=conf.passing,
                            factory=factory.LineFactory())
        return analyzer
                
    # help func to shorten create event file  
    def import_instrumented_module(function_under_test,converted_inp):
        from .rsc import instrumented  # TODO make this dynamic by connecting it with avix variable instrpath somehow
        # TODO : whyyyy reload breaky
        # for some reason reload broke this, maybe check this out later?
        #importlib.reload(instrumented)
        instrumented.sflkitlib.lib.reset()
        instrumented_function = getattr(instrumented, function_under_test)
        try:
            # # multiple args
            if (isinstance(converted_inp, list)):
                return instrumented_function(*converted_inp)
            else: 
                # result = instrumented_function(converted_inp)
                return instrumented_function(converted_inp)
        
        finally:
            instrumented.sflkitlib.lib.dump_events()
            #del instrumented