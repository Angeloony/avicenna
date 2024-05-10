# refine the import statements so they dont just import everything
import importlib
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple, Type

from debugging_framework.oracle import OracleResult
from fuzzingbook.Grammars import Grammar, is_valid_grammar
from isla.language import Formula, ISLaUnparser
from islearn.language import parse_abstract_isla
from islearn.learner import patterns_from_file
from returns.maybe import Maybe, Nothing, Some
from sflkit import *

from avicenna import Avicenna, feature_extractor
from avicenna.execution_handler import (BatchExecutionHandler,
                                        SingleExecutionHandler)
from avicenna.feature_collector import GrammarFeatureCollector
from avicenna.generator import (FuzzingbookBasedGenerator, Generator,
                                ISLaGrammarBasedGenerator,
                                MutationBasedGenerator)
from avicenna.input import Input
from avicenna.logger import LOGGER, configure_logging
from avicenna.monads import Exceptional, T, check_empty
from avicenna.pattern_learner import (AvicennaTruthTable,
                                      AvicennaTruthTableRow, AviIslearn,
                                      PatternLearner)
from avicenna.report import MultipleFailureReport, SingleFailureReport
from avicenna_formalizations import get_pattern_file_path


# maybe add oracle construction to avix separately as well to differentiate my contributions?
# add event files folder before init? 
class AviX(Avicenna):
    
    
    def __init__(
        self,
        desired_line: int,
        #call_function: Callable,
        put_path: str,
        min_precision: float,
        
        grammar: Grammar,
        oracle: Callable[[Input], OracleResult],
        initial_inputs: List[str],
        
        instr_path: str = 'rsc/instrumented.py',
        
        patterns: List[str] = None,
        max_iterations: int = 10,
        top_n_relevant_features: int = 2,
        pattern_file: Path = None,
        max_conjunction_size: int = 2,
        use_multi_failure_report: bool = True,
        use_batch_execution: bool = False,
        log: bool = False,
        feature_learner: feature_extractor.RelevantFeatureLearner = None,
        input_generator: Type[Generator] = None,
        pattern_learner: Type[PatternLearner] = None,
        timeout_seconds: Optional[int] = None,
        ):
        super().__init__(grammar=grammar,
            initial_inputs=initial_inputs,
            oracle=oracle,
            max_iterations=max_iterations,
        )
        
        self.desired_line = desired_line
        self._start_time = None
        self.patterns = patterns
        self.oracle = oracle
        self._max_iterations: int = max_iterations
        self._top_n: int = top_n_relevant_features
        self._targeted_start_size: int = 10
        self._iteration = 0
        self.timeout_seconds = timeout_seconds
        self.start_time: Optional[int] = None
        self._data = None
        self._all_data = None
        self._learned_invariants: Dict[str, List[float]] = {}
        self._best_candidates: Dict[str, List[float]] = {}
        self.min_precision = 0.6
        self.min_recall = 0.9
        
        # requires the path to PUT and the instrumented version of it. save tmp.py in the folder for now, delete when done
        AviX.instrument_avix(put_path=put_path, instr_path=instr_path)
        
        # importing instrumented function
        from avicenna.rsc import instrumented
        importlib.reload(instrumented)
        instrumented.sflkitlib.lib.reset()  
        
        # move this outside of avix, do this before and avix call
        # self.oracle = construct_oracle(
        #     program_under_test=instr.middle, # TODO : make the function name dynamic somehow
        #     call_function=call_function,
        #     timeout=10,
        #     line=desired_line,
        # ) # will be the line-Oracle, needs line and callable func and instrumentation
        
        
        
    # def run_instr(call_function, instr_file_function, inp):
    #     call_function(instr_file_function, inp)
        
    def avixplain(self) -> Optional[Tuple[Formula, float, float]]:
        
        if self.timeout_seconds is not None and self.start_time is None:
            self.start_time = int(time.time())

        new_inputs: Set[Input] = self.all_inputs.union(self.generate_more_inputs())
        while self._do_more_iterations():
            if self.timeout_seconds is not None:
                if int(time.time()) - self.start_time > self.timeout_seconds:
                    LOGGER.info("TIMEOUT")
                    raise TimeoutError(self.timeout_seconds)

            new_inputs = self._loop(new_inputs)
        print("before finalize")
        return self.finalize()

    """
        Create event-file for a given instrumented file and its input
    """

    def create_event_file(
            instrumented_function, #str # we call it dynamically in a sub-func
            #instr_path, #str
            inp, # string in
            conversion_func, #callable # convert the inp string to an input usable by the function
            event_path, #str # used to call the instrumented version of a function (needed bcs funcs have different amounts/types of variables needed for calls)
        ): 
        
        converted_inp = conversion_func(inp) # must always return a list!!
        
        # delete old event files first
        if os.path.exists(event_path):
            os.unlink(event_path)
        
        # # make sure that event-file is actually written in the rsc folder
        # TODO move the import into its own function maybe?
        os.environ['EVENTS_PATH'] = event_path        
        
        # this ends up creating the event file
        AviX.import_instrumented_module(instrumented_function, converted_inp)
          
          
    # help func to shorten create event file  
    def import_instrumented_module(function_under_test, converted_inp):
        from .rsc import \
            instrumented  # TODO make this dynamic by connecting it with avix variable instrpath somehow
        importlib.reload(instrumented)
        instrumented.sflkitlib.lib.reset()
        instrumented_function = getattr(instrumented, function_under_test)
        try:
            # multiple args
            return instrumented_function(*converted_inp)
        
        finally:
            instrumented.sflkitlib.lib.dump_events()
            del instrumented
            
            
    """ Instrumentation funcs and helper funcs"""
    # config for instrumentation, needs path for PUT and instrumentation, instr might be obsolete later
    def _get_config(
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
        # taken from sflkit
        return instrument_config(AviX._get_config(put_path=put_path, instr_path=instr_path))


    # import the instrumented function for later use
    def import_instrumented():
        import avicenna.rsc.instrumented
        importlib.reload(avicenna.rsc.instrumented)
        avicenna.rsc.instrumented.sflkitlib.lib.reset()
        return