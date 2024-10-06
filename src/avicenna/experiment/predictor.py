from avicenna.experiment.helper import import_fuzzed, import_csv, check_trigger, export_predictor

from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject

from isla.solver import ISLaSolver, SemanticError

"""
    PREDICTOR STUFF
"""
# false positive: determined true eventho false
# false negative: determined false eventho true
# true positive : determined true when true
# true negative : determined false when false  
def predictor(
    subject: Subject,
    relevant_attempts,
):  
    all_fuzzed = import_fuzzed('results/' + subject.name + '/fuzzed_predictor_nodupl.txt')    
    for line in subject.relevant_lines:
        print('predictor', subject.name, line)
        
        # allows me to test just 1 line/1 predictor
        subject_dict = import_csv('results/' + subject.name + '/' + str(line) + '_results.csv')
        for attempt in subject_dict:
            if str(attempt['Attempt']) in relevant_attempts:
                print(attempt['Attempt'])
                eval_dict = {
                'fpos' : [],
                'tpos' : 0,
                'tneg' : 0,
                'fneg' : [],
                }
                
                if (attempt['Constraint'] == None or attempt['Constraint'] == '' or 'Avicenna' in attempt['Constraint'] ):
                    continue
                
                else:
                    trigger_fuzzed = import_fuzzed('results/' + subject.name + '/' + str(line) +'_line_triggered_fuzz.txt')
                    solver = ISLaSolver(
                            grammar=subject.grammar,
                            formula=attempt['Constraint'],
                            enable_optimized_z3_queries=False,
                        )
                    
                    for input in all_fuzzed:
                        try:
                            solver.parse(inp=input)
                            if input in trigger_fuzzed:
                                eval_dict['tpos'] += 1
                            elif not(input in trigger_fuzzed):
                                eval_dict['fpos'].append(input)
                                
                                
                        except SemanticError:
                            if input in trigger_fuzzed:
                                eval_dict['fneg'].append(input)
                            elif not(input in trigger_fuzzed):
                                eval_dict['tneg'] += 1            

                    export_predictor(subject, line, eval_dict, all_fuzzed=all_fuzzed, trigger_fuzzed=trigger_fuzzed, attempt=attempt['Attempt'])
            else:
                continue
                    
    return eval_dict