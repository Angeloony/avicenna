import csv
import time
import logging
import string

from avicenna.avix import AviX
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from pandas import *
from isla.language import Formula
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
            'Constraint': ["No constraint has been found for min_precision 0.6 and min_recall 0.9."] * total_attempts,
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
                result_dict['Constraint'] = str(e)
                
                print('it failed im alive, just finished line ' + str(line) + ' run ' + str(attempt))
                continue
            
            end = time.time()
            if constraint:
                result_dict['Runtime'][attempt] = round(end - start, 3)
                result_dict['Readable_Constraint'][attempt] = constraint
                result_dict['Constraint'][attempt] = constraint[0]
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
            line=line
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
    with open(path, 'r') as data:
        csv_reader = csv.DictReader(data)
        data = [row for row in csv_reader]
    return data
    
    
def fuzz_with_constraints(subject: Subject, data: dict, line):
    # print(data['Constraint'])
    print("constraint")
    print(data)
    
    fuzzed_inputs = {
        'Fuzzed': [],
    }
    
    for constraint in data['Constraint']:
        fuzzed_inputs['Fuzzed'].append(constraint)
        for _ in range(0,100):
            try:
                solver = ISLaSolver(
                    grammar=subject.grammar,
                    #formula=data['Constraint'],
                    formula=constraint,
                    enable_optimized_z3_queries=False,
                )
                #print(solver.solve())
                fuzzed_inputs['Fuzzed'].append(solver.solve())
            except StopIteration:
                continue
    
    
    with open('results/middle/' + str(data['Line']) + '_fuzzed.txt', 'a+') as file:
        for item in fuzzed_inputs['Fuzzed']:
            file.write(f"{item}\n")
    
    return
    
    
"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    attempts_per_line = 2
    #run_subject(Subject(Subject.get_markup()), attempts_per_line)
    #run_subject(Subject(Subject.get_calculator()), attempts_per_line)
    # expression = Subject(Subject.get_expression())
    # expression = run_subject(expression, attempts_per_line)
    
    middle = Subject(Subject.get_middle())
    # middle_data = []
    middle = run_subject(middle, attempts_per_line)
    alt_data = middle.results
    middle_data = []
    for line in middle.relevant_lines:
        middle_data.append(import_csv('results/' + middle.name + '/' + str(line) + '_results.csv'))
    
    # print(len(middle_data))
    # print("middledata")
    # for item in middle_data:
    #     print(item)
    #print("altdata")
    # for item in alt_data:
    #     for other_item in alt_data:
    #         print('wa')
            
    print(alt_data[3])
    #print(working_line)
    relevant_constraints = []
    
    relevant_lines = {
        'Line': [],
        'Constraint': [],
    }
    
    for result_dict in middle.results:
        #print(result_dict['Constraint'])
        for constraint in result_dict['Constraint']:
            print(constraint)
            if isinstance(constraint, str):
                continue
            else:
                print(constraint)
                if constraint is Formula:
                    print("yay")
                    
                if constraint in relevant_constraints:
                    continue
                else:
                    relevant_lines['Line'] = result_dict['Line'][0]
                    relevant_lines['Constraint'].append(constraint)
                    relevant_constraints.append(constraint)
    
    print("relevant constraints after finding them hopefully lol")
    print(relevant_constraints)
    print(relevant_lines)
    for constraint_dict in relevant_lines:
        
        fuzz_with_constraints(middle, constraint_dict, 4)
    
    # for item in line_4:
    #     fuzz_with_constraints(middle, item)
    # for line_attempt_list in middle_data:
    #     for result_dict in line_attempt_list:
    #         print(result_dict['Attempt'])
    # TODO : get access to my dataframes, fuzz with them
    return

if __name__ == '__main__':
    main()