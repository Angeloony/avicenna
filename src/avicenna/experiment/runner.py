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
    
    df.to_csv('results/' + subject.name + str(line) + '_results.csv', sep=',', encoding='utf-8',)  
    
    
"""
    Main runner. Lets me adjust values, decide what programs to run etc.
"""
def main():
    calculator = Subject(Subject.get_calculator())
     
#     expression = Subject(Subject.get_expression())
    
    middle = Subject(Subject.get_middle())
    
    # markup = Subject(Subject.get_markup())
    
    runs = 2
    calculator.results = experiment(calculator, runs)
    # expression.results.append(experiment(expression, runs))
    #middle.results = experiment(middle, runs)
    # markup.results.append(experiment(markup, runs))
        
    # markup_results = experiment(subject=markup, total_runs=2)
    # print_subject_lines(markup)
    # print_subject_lines(middle)
    # print_subject_lines(expression)
    # print_subject_lines(calculator) 
    
    # test = [
    #     {'Runtime': [0.14, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.1, 0.11], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.1, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']}, 
    #     {'Runtime': [0.17, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
        
    #     {'Runtime': [0.1, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.1, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.1, 0.1], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [508.76, 1459.95], 'Precision': [0.8620689655172413, 0.7878787878787878], 'Recall': [1.0, 1.0], 'Constraint': ['''ExistsFormula(BoundVariable("elem_xy", "<html>"), Constant("start", "<start>"), PredicateFormula(("StructuralPredicate(name='inside', arity=2, eval_fun=<function in_tree at 0x7f68810809d0>)", 'BoundVariable("elem_xy", "<html>"), Constant("start", "<start>")')))''', '''ExistsFormula(BoundVariable("elem_xy", "<html>"), Constant("start", "<start>"), PredicateFormula(("StructuralPredicate(name='inside', arity=2, eval_fun=<function in_tree at 0x7f68810809d0>)", 'BoundVariable("elem_xy", "<html>"), Constant("start", "<start>")')))''']},
    #     {'Runtime': [0.61, 0.22], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
        
    #     {'Runtime': [337.28, 2711.09], 'Precision': [0.6666666666666667, 0.9069767441860466], 'Recall': [1.0, 1.0], 'Constraint': ['''ExistsFormula(BoundVariable("elem_xy", "<html>"), Constant("start", "<start>"), PredicateFormula(("StructuralPredicate(name='inside', arity=2, eval_fun=<function in_tree at 0x7f68810809d0>)", 'BoundVariable("elem_xy", "<html>"), Constant("start", "<start>")')))''', '''ExistsFormula(BoundVariable("elem_xy", "<RPAR>"), Constant("start", "<start>"), PredicateFormula(("StructuralPredicate(name='inside', arity=2, eval_fun=<function in_tree at 0x7f68810809d0>)", 'BoundVariable("elem_xy", "<RPAR>"), Constant("start", "<start>")')))''']},
    #     {'Runtime': [0.3, 0.23], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [769.96, 46.36], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.13, 0.14], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
        
    #     {'Runtime': [506.29, 260.67], 'Precision': [0.72, -1], 'Recall': [1.0, -1], 'Constraint': ['''ExistsFormula(BoundVariable("elem_xy", "<chars>"), Constant("start", "<start>"), PredicateFormula(("StructuralPredicate(name='inside', arity=2, eval_fun=<function in_tree at 0x7f68810809d0>)", 'BoundVariable("elem_xy", "<chars>"), Constant("start", "<start>")')))''', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.14, 0.11], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']},
    #     {'Runtime': [0.11, 0.12], 'Precision': [-1, -1], 'Recall': [-1, -1], 'Constraint': ['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']}]
    #export_results(calculator, calculator_results)
    #export_results(expression, expression_results)
    #export_results(middle, middle_results)
    export_results(calculator)
#     middle_results = ["[0.092, 0.055]","[-1, -1]","[-1, -1]","['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']"
# "[0.055, 0.052]","[-1, -1]","[-1, -1]","['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']"
# "[0.052, 0.051]","[-1, -1]","[-1, -1]","['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']"
# "[58.571, 73.413]","[1.0, 1.0]","[1.0, 1.0]","[ForallFormula(BoundVariable(""elem_1"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<z>""), BoundVariable(""elem_2"", ""<y>""), ))), ForallFormula(BoundVariable(""elem_1"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<z>""), BoundVariable(""elem_2"", ""<y>""), )))]"
# "[202.957, 464.997]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<z>""), BoundVariable(""elem_3"", ""<y>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<z>""), BoundVariable(""elem_3"", ""<y>""), ))))]"
# "[262.569, 229.439]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<x>""), BoundVariable(""elem_2"", ""<y>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<z>""), BoundVariable(""elem_3"", ""<y>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<x>""), BoundVariable(""elem_2"", ""<y>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<z>""), BoundVariable(""elem_3"", ""<y>""), ))))]"
# "[337.017, 482.165]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<z>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<x>""), BoundVariable(""elem_3"", ""<y>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<z>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<z>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<x>""), BoundVariable(""elem_3"", ""<y>""), ))))]"
# "[0.066, 0.053]","[-1, -1]","[-1, -1]","['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']"
# "[77.933, 135.816]","[1.0, 1.0]","[1.0, 1.0]","[ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<z>""), ))), ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<z>""), )))]"
# "[310.51, 205.291]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<z>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<x>""), BoundVariable(""elem_3"", ""<y>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<y>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<x>""), BoundVariable(""elem_2"", ""<y>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<y>""), BoundVariable(""elem_3"", ""<z>""), ))))]"
# "[299.848, 240.165]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<y>""), BoundVariable(""elem_3"", ""<z>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<y>""), BoundVariable(""elem_3"", ""<z>""), ))))]"
# "[274.983, 213.769]","[1.0, 1.0]","[1.0, 1.0]","[ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<x>""), BoundVariable(""elem_3"", ""<z>""), )))), ConjunctiveFormula(ForallFormula(BoundVariable(""elem_1"", ""<y>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_2"", ""<x>""), Constant(""start"", ""<start>""), SMTFormula('(>= (str.to_int elem_1) (str.to_int elem_2))', BoundVariable(""elem_1"", ""<y>""), BoundVariable(""elem_2"", ""<x>""), ))), ForallFormula(BoundVariable(""elem_0"", ""<x>""), Constant(""start"", ""<start>""), ExistsFormula(BoundVariable(""elem_3"", ""<z>""), Constant(""start"", ""<start>""), SMTFormula('(> (str.to_int elem_0) (str.to_int elem_3))', BoundVariable(""elem_0"", ""<x>""), BoundVariable(""elem_3"", ""<z>""), ))))]"
# "[0.051, 0.047]","[-1, -1]","[-1, -1]","['No constraint has been found for min_precision 0.6 and min_recall 0.9.', 'No constraint has been found for min_precision 0.6 and min_recall 0.9.']"
#     ]
    #print(test)

if __name__ == '__main__':
    main()