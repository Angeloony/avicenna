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
    total_attempts: int,
):    
    all_results = []
    
    for line in subject.relevant_lines:
        result_dict = {
            'Attempt': [-1] * total_attempts,
            'Runtime': [-1] * total_attempts,
            'Precision': [-1] * total_attempts,
            'Recall': [-1] * total_attempts,
            'Constraint': ["No constraint has been found for min_precision 0.6 and min_recall 0.9."] * total_attempts,
            'Readable_Constraint': ["No constraint has been found for min_precision 0.6 and min_recall 0.9."] * total_attempts,
        }
        
        for attempt in range(0, total_attempts):
            try:            
                start = time.time()
                result_dict['Attempt'][attempt] = attempt + 1
                constraint = explain_line(line=line, subject=subject) 

            except AssertionError as e:
                end = time.time()
                result_dict['Runtime'][attempt] = round(end - start, 3)
                # TODO doublecheck this
                result_dict['Constraint'] = e
                
                print('it failed im alive, just finished line ' + str(line) + ' run ' + str(attempt))
                continue
            
            end = time.time()
            if constraint:
                result_dict['Runtime'][attempt] = round(end - start, 3)
                result_dict['Readable_Constraint'][attempt] = str(constraint[0])
                result_dict['Constraint'][attempt] = str(constraint)[1:-11]
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
    
    for line in subject.relevant_lines:
        for result in subject.results: 
            #print("export result: ")
            print(result)
            export_dataframe_to_csv(
                subject=subject,
                results=result,
                line=line
            )
        
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
    print("dataframe")
    print(df)
    
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
    
"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    attempts_per_line = 10
    #run_subject(Subject(Subject.get_markup()), attempts_per_line)
    #run_subject(Subject(Subject.get_calculator()), attempts_per_line)
    #run_subject(Subject(Subject.get_expression()), attempts_per_line)
    
    middle = Subject(Subject.get_middle())
    # middle_data = []
    middle = run_subject(middle, attempts_per_line)
    
    middle_data = []
    for line in middle.relevant_lines:
        middle_data.append(import_csv('results/' + middle.name + '/' + str(line) + '_results.csv'))
    for item in middle_data:
        for thing in item:
            print(thing)
    
    return

if __name__ == '__main__':
    main()