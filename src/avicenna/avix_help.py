from importlib import resources
from pathlib import Path

from sflkit import instrument_config
from sflkit.config import Config
from sflkit.analysis import factory
from sflkit.analysis.analyzer import Analyzer
from sflkitlib.lib import reset, dump_events

""" Instrumentation funcs and helper funcs"""

# Embedded SFLKit's instrumentation into AviX
def instrument(put_path:str, instr_path: str, ):
    # taken from sflkit
    return instrument_config(
        get_sfl_config(put_path=put_path,
                       instr_path=instr_path))


# get the path to source in avicenna, from where we will import the instr file
def get_avicenna_rsc_path() -> Path:
    with resources.path('avicenna', 'rsc') as p:
        return Path(p)
    
    
# config for instrumentation, needs path for PUT and instrumentation, instr might be obsolete later
def get_sfl_config(          
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
def import_instrumented(function_under_test,converted_inp):
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