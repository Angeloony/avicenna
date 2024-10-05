import csv
import time
import logging
import string
from typing import List, Dict

from avicenna.experiment.runner_helper import *
from avicenna.avix import AviX
from avicenna.avix_help import instrument
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from avicenna.experiment.producer import producer
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
    #     relevant_attempts=['1', '2'], # for line 6
    #     # relevant_attempts= ['1', '3','4'], # line 7
    #     # relevant_attempts= ['1'] # rest of the lines, exclude 1, 2, 3, 8, 13
    #     subject=middle,
    # )
    # fuzz_subject(
    #     subject=calculator,
    #     relevant_attempts= ['1', '2', '3'] # line 8
    #     relevant_attempts= ['1', '2'] # line 9
    #     relevant_attempts= ['1', '3', '4'] # line 12
    #     relevant_attempts= ['1', '2'] # line 15
    #     relevant_attempts= ['1'] # line 20, 28,
    #     relevant_attempts= ['1', '10'] # line 24
    # )
    # fuzz_subject(
    #     subject=markup,
    #     relevant_attempts= ['1', '6'] # line 8
    #     relevant_attempts= ['1'] # line 10
    #     relevant_attempts= ['9'] # line 14
    # )
    # fuzz_subject(
    #     subject=markup,
    #     relevant_attempts= ['1'] # line 40, 59, 73, 85, 93, 97, 
    #     relevant_attempts= ['1', '2'] # line 95
    #     relevant_attempts= ['1', '3', '8', '9'] # line 105
    #     relevant_attempts= ['1', '7'] # line 107
    #     relevant_attempts= ['1', '2', '4'] # line 109
    # )
        
    #check_sem_fuzz(calculator)
    
    # PREDICTOR SECTION
    # ***********************************
    # predictor(markup)
    # predictor(expression)
    # predictor(calculator)
    predictor(middle)
    
    # TODO : DO EXPRESSION AND MIDDLE RUN OVER NIGHT
    #ground_truth(markup, import_fuzzed('results/markup/fuzzed_predictor_nodupl.txt'))
    #ground_truth(expression, import_fuzzed('results/expression/fuzzed_predictor_nodupl.txt'))
    #ground_truth(middle, import_fuzzed('results/middle/fuzzed_predictor_nodupl.txt'))
    #ground_truth(calculator, import_fuzzed('results/calculator/fuzzed_predictor_nodupl.txt'))
    # eval_dict = predict_fuzzed(markup)
    # remove_duplicate_lines('results/' + middle.name + '/fuzzed_predictor.txt', 'results/' + middle.name + '/fuzzed_predictor_nodupl.txt')
    # remove_duplicate_lines('results/' + markup.name + '/fuzzed_predictor.txt', 'results/' + markup.name + '/fuzzed_predictor_nodupl.txt')
    # remove_duplicate_lines('results/' + expression.name + '/fuzzed_predictor.txt', 'results/' + expression.name + '/fuzzed_predictor_nodupl.txt')
    # remove_duplicate_lines('results/' + calculator.name + '/fuzzed_predictor.txt', 'results/' + calculator.name + '/fuzzed_predictor_nodupl.txt')
    #predictor(markup)
    # predictor(expression)
    # predictor(calculator)
    
                
    #print(inputs)
    #print(eval_dict)
  

if __name__ == '__main__':
    main()