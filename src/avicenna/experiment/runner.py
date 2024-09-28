import csv
import time
import logging

from avicenna.avix import AviX
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from pandas import * 

        
def print_subject_lines(subject):
    print("[")
    for i in range(1, subject.relevant_lines + 1):
        print(str(i) + ", ", end='')
    print("]")
    
"""
    Runs avix.explain on the given subject for each line in the program. 
    
    Lines that have missing test cases (either no failure or no passing), are returned as empty. 
    Lines without a return with high enough scores come back as None. 
    
    Time is measured for each line. 
"""
def experiment(
    subject: Subject,
    total_runs: int,
):    
    all_results = []
    print(len(subject.relevant_lines))
    
    for line in subject.relevant_lines:
        result_dict = {
            'Runtime': [-1] * total_runs,
            'Precision': [-1] * total_runs,
            'Recall': [-1] * total_runs,
            'Constraint': ["No constraint has been found for min_precision 0.6 and min_recall 0.9."] * total_runs,
        }
        
        for run in range(0, total_runs):
            try:            
                start = time.time()
                constraint = explain_line(line=line, subject=subject) 

            except AssertionError as e:
                end = time.time()
                result_dict['Runtime'][run] = round(end - start, 3)
                # TODO doublecheck this
                result_dict['Constraint'] = e
                
                print('it failed im alive, just finished line ' + str(line) + ' run ' + str(run))
                continue
            
            end = time.time()
            if constraint:
                result_dict['Runtime'][run] = round(end - start, 3)
                result_dict['Constraint'][run] = constraint[0]
                result_dict['Precision'][run] = round(constraint[1], 2)
                result_dict['Recall'][run] = round(constraint[2], 2)
                
            else:
                result_dict['Runtime'][run] = round(end - start, 3)
            
            print('it worked im alive, just finished line ' + str(line) + ' run ' + str(run))
            
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
        )
        
        logging.basicConfig(filename='logs/' + subject.name + str(line) + '.log', filemode='w', encoding='utf-8', level=logging.DEBUG, force=True)
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
    line = 0
    for result in subject.results: 
        print("export result: ")
        print(result)
        print_dataframe(subject, result, subject.relevant_lines[line])
        line = line + 1
        
"""
    Export results from avix.explain of a given run into a csv-file. 
    
    Columns are constraints and timers, rows are investigated lines.
"""
def print_dataframe(
    subject: Subject,
    results: dict,
    line: str
):
    df = DataFrame(data=results,)
    print("dataframe")
    print(df)
    
    df.to_csv('results/' + subject.name + '/' + str(line) + '_results.csv', sep=',', encoding='utf-8',)  
    
    
"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    calculator = Subject(Subject.get_calculator())
     
    expression = Subject(Subject.get_expression())
    
    middle = Subject(Subject.get_middle())
    
    markup = Subject(Subject.get_markup())
    
    runs = 10
    calculator.results = experiment(calculator, runs)
    expression.results = experiment(expression, runs)
    middle.results = experiment(middle, runs)
    markup.results = experiment(markup, runs)
    
    export_results(calculator)
    export_results(expression)
    export_results(middle)
    export_results(markup)

if __name__ == '__main__':
    main()