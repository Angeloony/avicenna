import csv
import time
import logging

from avicenna.avix import AviX
from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject
from pandas import * 

"""
    Runs avix.explain on the given subject for each line in the program. 
    
    Lines that have missing test cases (either no failure or no passing), are returned as empty. 
    Lines without a return with high enough scores come back as None. 
    
    Time is measured for each line. 
"""
def experiment(
    subject: Subject,
    iteration: int,
):
    results = {}
    timer_results = {}
    # check all lines and run tests. init inputs should be provided to trigger each possible line
    for line in range(1, subject.total_lines + 1):
        start = time.time()
        results['Line ' + str(line)] = run_single_experiment(line=line, subject=subject) 
        end = time.time()
        
        results['Line ' + str(line)].append(end - start)
        #timer_results[str(line)] = end - start
        
        print('im alive, just finished line ' + str(line))
            
    return results


"""
    Run a single line analysis for a given subject.
    
    I.e. line = 7, subject = middle.
    Middle will be investigated, checking what inputs trigger line 7.
"""        
def run_single_experiment(
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
            #max_conjunction_size=6,
        )   
        
        logging.basicConfig(filename='logs/' + subject.name + str(line) + '.log', filemode='w', encoding='utf-8', level=logging.INFO, force=True)
        best_invariant = avix.explain()
        
        if best_invariant == None:
            return ["No constraint was found for recall 0.9 and precision 0.6."]
        #     avix.min_precision = 0.3

        #     logging.basicConfig(filename='logs/' + subject.name + str(line) + '.log', filemode='w', encoding='utf-8', level=logging.INFO, force=True)
        #     best_invariant = avix.explain()
        #     if best_invariant == None:  
        #         best_invariant = "No invariant was found for recall 0.9 and precision = 0.6 or precision = 0.3."
        #         return [best_invariant]
    
    except AssertionError as e:
        return [str(e)] # double check the assertionerror in list
    
    # final = []
    # for result in best_invariant:
    #     final.append(result)
        
    return [str(best_invariant)]
 
 
"""
    Export results from avix.explain of a given run into a csv-file. 
    
    Columns are constraints and timers, rows are investigated lines.
"""
def export_results(
    subject: Subject,
    results: dict,
):
    for key, item in results:
        print(key)
        print(item)
        
    df = DataFrame(data=results,)
    print(df)
    
    df.to_csv('results/' + subject.name + '_results.csv', sep='\t', encoding='utf-8',)  
    
    
"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    calculator = Subject(Subject.get_calculator())
    calculator_results = []
     
    expression = Subject(Subject.get_expression())
    expression_results = []
    
    middle = Subject(Subject.get_middle())
    middle_results = []
    
    markup = Subject(Subject.get_markup())
    markup_results = []
    
    
    for i in range(1,2):
        #calculator_results.append(experiment(calculator, i))
        #expression_results.append(experiment(expression, i))
        #middle_results.append(experiment(middle, i))
        markup_results.append(experiment(markup, i))

    #export_results(calculator, calculator_results)
    #export_results(expression, expression_results)
    #export_results(middle, middle_results)
    print(markup_results)
    for result in markup_results: 
        
        export_results(markup, result)


if __name__ == '__main__':
    main()