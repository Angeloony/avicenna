import csv
import time
import logging
import string
from pandas import DataFrame

from avicenna.avix import AviX
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject

from fuzzingbook.Grammars import EXPR_EBNF_GRAMMAR, convert_ebnf_grammar, Grammar, Expansion
from fuzzingbook.Grammars import simple_grammar_fuzzer, is_valid_grammar, exp_string
from fuzzingbook.GrammarFuzzer import GrammarFuzzer

from isla.language import Formula, ISLaUnparser
from isla.solver import ISLaSolver
from isla.derivation_tree import DerivationTree
    
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
                # print("unparsed constraint")
                # print(ISLaUnparser(constraint[0]).unparse())
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
        raise e # double check the assertionerror in list
    
    # this happens on a successful run
    return best_invariant
 

def export_results(subject: Subject):
    line = 1
    for result in subject.results: 
        #print("export result: ")
        #print(result)
        export_dataframe_to_csv(
            subject=subject,
            results=result,
            line=result['Line'][0]
        )
        line = line + 1
        
        
"""
    Export results from avix.explain of a given run into a csv-file. 
    
    Columns are constraints and timers, rows are investigated lines.
"""
def export_dataframe_to_csv(
    subject: Subject,
    results: dict,
    line: str
):
    df = DataFrame(data=results,)
    # print("dataframe")
    # print(df)
    
    df.to_csv('results/' + subject.name + '/' + str(line) + '_results.csv', sep=',', encoding='utf-8',)  
    
    
def run_subject(subject: Subject, runs: int):
    subject.results = experiment(subject, runs)
    export_results(subject)
    return subject


def import_csv(path):
    # read csv file to a list of dictionaries
    print(path)
    with open(path, 'r') as data:
        csv_reader = csv.DictReader(data)
        data = [row for row in csv_reader]
    return data
    
    
 
    
# makes 1000 inputs for a subject based on its grammar
def predictor(subject: Subject):
    
    subject_fuzzer = GrammarFuzzer(grammar=subject.grammar)
    
    for _ in range(0,1000):
        with open('results/' + subject.name + '/fuzzed_predictor.txt', 'a+') as file:
            file.write(f"{subject_fuzzer.fuzz()}\n")
    
    return


def fuzz_subject(
    subject: Subject,
):
    for line in subject.relevant_lines:
        subject_dict = import_csv('results/' + subject.name + '/' + str(line) + '_results.csv')
        for attempt in subject_dict:
            print("ATTEMPT: ")
            print(attempt)
            if attempt['Constraint'] == None or 'Avicenna' in attempt['Constraint'] or attempt['Constraint'] == '':
                print("failed")
                print(attempt['Constraint'])
                continue
            else:
                print("passed")
                print(attempt['Constraint'])
                fuzz_with_constraints(subject, attempt['Constraint'], line)


# pass constraint as string
def fuzz_with_constraints(
    subject: Subject,
    constraint,
    line,
):
    fuzzed_inputs = {
        'Fuzzed': [],
    }
    
    fuzzed_inputs['Fuzzed'].append(constraint)
    
    # 20 inputs per constraint
    for _ in range(0,30):
        
        try:
            solver = ISLaSolver(
                grammar=subject.grammar,
                formula=constraint,
                enable_optimized_z3_queries=False,
            )
            
            fuzzed_inputs['Fuzzed'].append(solver.solve())
            
        except StopIteration:
            continue
    
    with open('results/' + subject.name + '/' + str(line) + '_fuzzed.txt', 'a+') as file:
        for item in fuzzed_inputs['Fuzzed']:
            file.write(f"{item}\n")
    
    return
   
    
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
    # expression = run_subject(expression, attempts_per_line)
    #calculator = run_subject(calculator, attempts_per_line)
    #markup = run_subject(markup, attempts_per_line)
    # middle = run_subject(middle, attempts_per_line)
    
    
    
    # PRODUCER SECTION
    # ***********************************
    # fuzz_subject(
    #     subject=middle,
    # )
    fuzz_subject(
        subject=calculator,
    )
    # fuzz_subject(
    #     subject=markup,
    # )
    # fuzz_subject(
    #     subject=expression,
    # )
        
    # PREDICTOR SECTION
    # TODO : Read fuzzed inputs from file
    # TODO : run through oracle, 
    # ***********************************
    # predictor(markup)
    # predictor(expression)
    # predictor(calculator)
    # predictor(middle)
    
    #fuzz_with_constraints(subject=middle, constraint=str(constraint), line=)
    # TODO : 
    # for result in middle.results:
    #     it = 0
    #     for constraint in result['Constraint']:
    #         if isinstance(constraint, Formula):
    #             fuzz_with_constraints(
    #                 middle,
    #                 constraint,
    #                 result['Line'][0],
    #                 result['Readable_Constraint'][it],
    #             )
    #         it = it + 1
    # return

if __name__ == '__main__':
    main()