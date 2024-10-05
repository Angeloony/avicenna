from avicenna.experiment.runner_helper import *
from avicenna.avix_help import instrument
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from avicenna.experiment.runner_helper import import_csv, import_fuzzed

from isla.solver import ISLaSolver


def producer(
    subject: Subject,
    relevant_attempts, 
):
    # These are the attempts that have returned different constraints.
    # We are only interested in returning these.
    for line in subject.relevant_lines:
        subject_dict = import_csv('results/' + subject.name + '/' + str(line) + '_results.csv')
        
        for attempt in subject_dict:
            if (attempt['Constraint'] == '' or
                attempt['Constraint'] == None or
                'Avicenna' in attempt['Constraint']):
                continue
            else:
                #print("hi", attempt['Attempt'])
                if attempt['Attempt'] in relevant_attempts:
                    semantic_fuzz(subject, attempt['Constraint'], line, 1000, attempt['Attempt'])


# pass constraint as string
def semantic_fuzz(
    subject: Subject,
    constraint,
    line,
    amount,
    attempt
):
    fuzzed_inputs = {
        'Fuzzed': [],
    }
    fuzzed_inputs['Fuzzed'].append('Constraint Begin: \n'+ constraint + '\nConstraint End.')
    for _ in range(0,amount):
        try:
            solver = ISLaSolver(
                grammar=subject.grammar,
                formula=constraint,
                enable_optimized_z3_queries=False,
            )
            fuzz = solver.solve()
            if not(fuzz in fuzzed_inputs['Fuzzed']):
                fuzzed_inputs['Fuzzed'].append(fuzz)
            
        except StopIteration:
            continue
    
    with open('results/' + subject.name + '/' + str(line) + '_Attempt'+ str(attempt) +'_producer.txt', 'a+') as file:
        for item in fuzzed_inputs['Fuzzed']:
            file.write(f"{item}\n")
    
    return



def check_producer(
    subject:Subject
):
    instrument(
        put_path=subject.put_path,
        instr_path=str(get_avicenna_rsc_path()) + '/instrumented.py',
    )
    
    for line in subject.relevant_lines:
        
        subject_oracle = construct_oracle(
            program_under_test=subject.first_func,
            inp_converter=subject.converter,
            line = line,
            resource_path=str(get_avicenna_rsc_path()),
            put_path=subject.put_path,
        )
        inputs = import_fuzzed(
            'results/' + subject.name + '/' + str(line) + '_produce.txt'
        )
        parsing_constraint = False
        after_first_run = False
        
        for input in inputs:
            
            if 'Constraint Begin' in input:
                if after_first_run == True:
                    export_producer(subject, line, eval_dict,)
                    
                parsing_constraint = True
                after_first_run = True
                eval_dict = {
                    'constraint' : [],
                    'triggering_fuzz' : [],
                    'non_triggering_fuzz' : [],
                }
            
            elif 'Constraint End' in input:
                parsing_constraint = False
            
            elif parsing_constraint == False:
                if subject_oracle(input) == OracleResult.FAILING:
                    eval_dict['triggering_fuzz'].append(input)
                else:
                    eval_dict['non_triggering_fuzz'].append(input)
                    
            elif parsing_constraint == True:
                eval_dict['constraint'].append(input)

    export_producer(subject, line, eval_dict)
