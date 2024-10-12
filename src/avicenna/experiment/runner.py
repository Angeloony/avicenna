import csv
import time
import logging
import string
from pandas import *
import statistics 
import numpy
from typing import List, Dict
from avicenna.rsc.expression import *
from avicenna.rsc.calculator import main as pain
from avicenna.experiment.helper import *
from avicenna.avix import AviX
from avicenna.avix_help import instrument
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from avicenna.experiment.producer import producer, check_producer
from avicenna.experiment.predictor import predictor

from isla.language import Formula, ISLaUnparser
    
"""
    Runs avix.explain on the given subject for each line in the program. 
    
    Lines that have missing test cases (either no failure or no passing), are returned as empty. 
    Lines without a return with high enough scores come back as None. 
    
    Time is measured for each line. 
"""
def experiment(
    subject: Subject,
    total_attempts: int,
):    
    all_results = []
    
    for line in subject.relevant_lines:
        result_dict = {
            'Attempt': [-1] * total_attempts,
            'Runtime': [-1] * total_attempts,
            'Precision': [-1] * total_attempts,
            'Recall': [-1] * total_attempts,
            'Line': [-1] * total_attempts,
            'Constraint': [None] * total_attempts,
            'Readable_Constraint': ["No constraint has been found for min_precision 0.6 and min_recall 0.9."] * total_attempts,
        }
        
        for attempt in range(0, total_attempts):
            try:     
                result_dict['Attempt'][attempt] = attempt + 1
                result_dict['Line'][attempt] = line       
                start = time.time()
                constraint = explain_line(line=line, subject=subject) 

            except AssertionError as e:
                end = time.time()
                result_dict['Runtime'][attempt] = round(end - start, 3)
                # TODO doublecheck this
                result_dict['Constraint'][attempt] = None
                result_dict['Readable_Constraint'][attempt] = str(e)
                
                print('it failed im alive, just finished line ' + str(line) + ' run ' + str(attempt))
                continue
            
            end = time.time()
            
            if constraint:
                result_dict['Runtime'][attempt] = round(end - start, 3)
                
                result_dict['Readable_Constraint'][attempt] = str(constraint)[1:-11]
                # check formula_from_string? smth like that, check to read formula to parse for fuzzing
                result_dict['Constraint'][attempt] = ISLaUnparser(constraint[0]).unparse()
                result_dict['Precision'][attempt] = round(constraint[1], 2)
                result_dict['Recall'][attempt] = round(constraint[2], 2)
                
            else:
                result_dict['Runtime'][attempt] = round(end - start, 3)
            
            print('it worked im alive, just finished line ' + str(line) + ' run ' + str(attempt))
            
        all_results.append(result_dict)
    
    return all_results


"""
    Run a single line analysis for a given subject.
    
    I.e. line = 7, subject = middle.
    Middle will be investigated, checking what inputs trigger line 7.
"""        
def explain_line(
    line : int, 
    subject : Subject,
):
    avix_oracle = construct_oracle(
        program_under_test=subject.first_func,
        inp_converter=subject.converter,
        line = line,
        resource_path=str(get_avicenna_rsc_path()),
        put_path=subject.put_path,
    )
    # in case there is no failure inducing input given, remove from pool essentially
    try:
        avix = AviX(
            grammar=subject.grammar,
            initial_inputs=subject.inputs,
            oracle=avix_oracle,
            max_iterations=10,
            top_n_relevant_features=3,
            put_path= subject.put_path,
            min_recall=0.9,
            min_min_specificity=0.6,
            max_conjunction_size=4
        )
        
        logging.basicConfig(filename='logs/' + subject.name + str(line) + '.log', filemode='w', encoding='utf-8', level=logging.INFO, force=True)
        best_invariant = avix.explain()
        
        # this happens if no invariant was found
        if best_invariant == None:
            return None
    
    # this happens if no passing/failing input was given
    except AssertionError as e:
        raise e 
    
    # this happens on a successful run
    return best_invariant
 

def run_subject(subject: Subject, runs: int):
    subject.results = experiment(subject, runs)
    export_results(subject)
    
    return subject

def get_runtimes(subject:Subject):
    runtimes = []
    final = []
    for line in subject.relevant_lines:
        df = DataFrame(data=import_csv('results/'+ subject.name +'/'+str(line)+'_results.csv'))
        #print(df)
        runtimes.append(df['Runtime'])
        #print(runtimes)
    
    for attempt in runtimes:
        #print(attempt)
        for runtime in attempt:
            #print(runtime)
            if runtime == '-1.0' or runtime == '-1':
                final.append(0)
            else:
                final.append((float(runtime)))
    final.sort()
    return final

"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    # PREAMBLE
    # ***************************
    attempts_per_line = 10
    
    expression = Subject(Subject.get_expression())
    calculator = Subject(Subject.get_calculator())
    markup = Subject(Subject.get_markup())
    middle = Subject(Subject.get_middle())
    
    # RUNNER SECTION
    # ****************************
    #expression = run_subject(expression, attempts_per_line)
    #calculator = run_subject(calculator, attempts_per_line)
    #markup = run_subject(markup, attempts_per_line)
    #middle = run_subject(middle, attempts_per_line)
    
    
    
    # PRODUCER SECTION
    # ***********************************
    # producer(
    #     # relevant_attempts=['1', '2'], # for line 6
    #     # relevant_attempts= ['1', '3','4'], # line 7
    #     relevant_attempts= ['4'], # rest of the lines, exclude 1, 2, 3, 8, 13
    #     subject=middle,
    # )
    # producer(
    #     subject=calculator,
    #     # relevant_attempts= [] # line 8
    #     # relevant_attempts= [] # line 9
    #     # relevant_attempts= [] # line 12
    #     # relevant_attempts=  # line 15
    #     # relevant_attempts= [# line 20, 28,
    #     relevant_attempts= ['10']#] # line 24
    # )
    #producer(
    #     subject=markup,
    #     relevant_attempts= ['6']#] # line 8
    #     # relevant_attempts= [] # line 10
    #     # relevant_attempts= [] # line 14
    # )
    # producer(
    #     subject=expression,
    #     relevant_attempts= ['3',] # line 40, 59, 73, 85, 93, 97, 
    #     # relevant_attempts= [] # line 95
    #     #relevant_attempts= ['4'] # line 87
    #     # relevant_attempts= [] # line 107
    #     # relevant_attempts= [] # line 109
    # )
    
    # check_producer(
    #     expression,
    #     ['2']
    # )
        
    #check_sem_fuzz(calculator)
    
    # PREDICTOR SECTION
    # ***********************************
    # predictor(markup)
    # predictor(expression)
    # predictor(calculator)
    #ground_truth(expression, import_fuzzed('results/expression/fuzzed_predictor_nodupl.txt'))

    # # attempt = '2'
    predictor(
        subject=expression,
        relevant_attempts=['4',],
        predict_file_name='_line_triggered_fuzz',
        total_file_name='fuzzed_predictor_nodupl'
    )
    
    # runtimes = get_runtimes(subject=expression)
    # print(runtimes)
    # print(statistics.median(runtimes), numpy.percentile(runtimes, 25), numpy.percentile(runtimes, 75), numpy.min(runtimes), numpy.max(runtimes), )
    # print(numpy.percentile(runtimes, 75) - numpy.percentile(runtimes, 25), numpy.percentile(runtimes, 75) - numpy.percentile(runtimes, 25) + numpy.percentile(runtimes, 75))
    # # TODO : DO EXPRESSION AND MIDDLE RUN OVER NIGHT
    # #ground_truth(expression, import_fuzzed('results/expression/fuzzed_predictor_nodupl.txt'))
    # for line in markup.relevant_lines:
    #     remove_duplicate_lines(
    #         'results/markup/' + str(line) + '_producer_line_triggered_fuzz.txt',
    #         'results/markup/' + str(line) + '_producer_line_triggered_fuzznodupl.txt')
        
    #ground_truth(middle,import_fuzzed('results/middle/fuzz_producer.txt'))
    #ground_truth(markup,import_fuzzed('results/markup/fuzz_producer.txt'))
    #ground_truth(calculator,import_fuzzed('results/calculator/fuzz_producer.txt'))
    #ground_truth(expression,import_fuzzed('results/expression/fuzz_producer.txt'))
    #print(inputs)
    #print(eval_dict)
  

if __name__ == '__main__':
    main()