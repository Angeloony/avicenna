import csv

from pandas import DataFrame

from avicenna.oracle_construction import * 
from avicenna.experiment.experiment import Subject

from avicenna.avix_help import instrument

from fuzzingbook.GrammarFuzzer import GrammarFuzzer


"""
    _.~* FILE MANAGEMENT FUNCTIONS *~._

    ~* import_csv *~
    
    ~ Inputs ~
    path : Path to our results folder containing all of our data.
    
    ~ Outputs ~
    Attempt   : We run each line-explanation 10 times. Attempt is the number of the try.
    Runtime   : Duration of the attempt.
    Precision : Avicenna's evaluated Precision score for a constraint.
    Recall    : Avicenna's evaluated Recall score for a constraint.
    Line      : What line was investigated?
    Constraint: Unparsed constraint, used for semantic fuzzing.
    Readable  : Constraint returned as string OR error msg if applicable.
    
    Imports the saved constraints with following information:
    
"""
def import_csv(path):
    # read csv file to a list of dictionaries
    with open(path, 'r') as data:
        csv_reader = csv.DictReader(data)
        data = [row for row in csv_reader]
    return data


"""
    ~* import_fuzzed *~
    
    ~ Inputs ~
    path : Path to the file containing fuzzed inputs from earlier runs.
    
    ~ Outputs ~
    List of inputs saved in the intermediary save file path.
    
    Imports a .txt file. Usually used for saving fuzzed inputs between experimentation runs as an intermediary save.
    
"""
def import_fuzzed(path):
    inputs = []
    with open(path, 'r') as file:
        for line in file:
            # Strip newline characters and append the line to the list
            inputs.append(line.strip())
    return inputs   


""" export function for the initially mined constraints to a csv file. """    
def export_results(subject: Subject):
    line = 1
    for result in subject.results:
        df = DataFrame(data=result,)
        df.to_csv(
            'results/' + subject.name + '/' + str(result['Line'][0]) + '_results.csv', sep=',', encoding='utf-8',
        ) 
        line = line + 1
      
        
""" 
    ~* export_predictor *~
    
    ~ Inputs ~
    subject: Our test subject, containing all relevant data. Defined in the Subject class.
    line: Current line of which we use the constraint to predict the behavior of our randomly fuzzed inputs.
    eval_dict: Dict containing all predicted inputs. Depending on if they were correctly predicted or not, they are classified as tpos, fpos, tneg, fneg.
    all_fuzzed: All grammar-fuzzed inputs (without duplicates).
    trigger_fuzzed: All grammar-fuzzed inputs that triggered the given line. 
    attempt: Attempt in csv-file, helps to orient for duplicate constraints.
    
    ~ Outputs ~
    txt. file containing the collected prediction stats for the given line when using the constraint from the given attempt number.
"""
def export_predictor(
    subject:Subject,
    line,
    eval_dict,
    all_fuzzed,
    trigger_fuzzed,
    attempt
):  
    with open('results/' + subject.name + '/' + str(line) + '_Attempt'+str(attempt)+'_predictor_results.txt', 'a+') as file:
        file.write(f"----------------NEW ATTEMPT #{attempt}----------------\n")
       
        for item in eval_dict:
            file.write(f"{item}\n")
            
            if item == 'tpos':
                file.write(f"{eval_dict[item]} were correctly classified as True Positive out of {len(trigger_fuzzed)} True Positives.\n")
            
            if item == 'tneg':
                file.write(f"{eval_dict[item]} were correctly classified as True Negative out of {len(all_fuzzed) - len(trigger_fuzzed)} True Negatives.\n")
            
            if item == 'fpos':
                file.write(f"{len(eval_dict[item])} were wrongly classified as False Positive out of {len(all_fuzzed) - len(trigger_fuzzed)} True Negatives.\nThe wrongly classified inputs were: {eval_dict[item]}.\n")
           
            if item == 'fneg':
                file.write(f"{len(eval_dict[item])} were wrongly classified as False Negative out of {len(trigger_fuzzed)} True Positives.\nThe wrongly classified inputs were: {eval_dict[item]}.\n\n")
    
                file.write(f"\n{len(all_fuzzed)} unique inputs were grammar-fuzzed in total.")
   
   
""" 
    ~* export_producer *~
    
    ~ Inputs ~
    subject: Our test subject, containing all relevant data. Defined in the Subject class.
    line: Current line for which we semantically fuzzed in our producer step.
    eval_dict: Dict containing all of our unique semantically fuzzed inputs, classified as triggering_fuzz or non_triggering_fuzz.
    
    ~ Outputs ~
    txt. file containing the collected prediction stats for the given line when using the constraint from the given attempt number.
"""           
def export_producer(
    subject:Subject,
    line,
    eval_dict,
    attempt
):
    unique_inputs = len(eval_dict['triggering_fuzz']) + len(eval_dict['non_triggering_fuzz'])
    
    with open('results/' + subject.name + '/' + str(line) +'_Attempt'+str(attempt)+'_producer_results.txt', 'a+') as file:
        file.write(f"----------------NEW ATTEMPT #{attempt}----------------\n")
        
        for item in eval_dict:
            file.write(f"{item}\n")
            
            if item == 'constraint':
                file.write(f"{eval_dict[item]}\nThe following stats were collected.\n{unique_inputs} out of 1,000 originally fuzzed inputs were unique.\n") 
            
            if item == 'triggering_fuzz':
                file.write(f"{len(eval_dict[item])} correctly triggered the line out of {unique_inputs} unique fuzzed inputs.\nThese are the inputs: {eval_dict[item]}.\n")
            
            if item == 'non_triggering_fuzz':
                file.write(f"{len(eval_dict[item])} incorrectly did NOT trigger the line out of {unique_inputs} unique fuzzed inputs.\nThese are the inputs: {eval_dict[item]}.\n")
  
     
""" removed duplicate fuzzed entries"""
def remove_duplicate_lines(input_file, output_file):
    with open(input_file, 'r') as infile:
        # Use a set to track unique lines
        unique_lines = set(infile.readlines())
    
    with open(output_file, 'w') as outfile:
        # Write the unique lines to the output file
        outfile.writelines(unique_lines)           
 
                
""" 
    _.~* PREDICTOR SETUP FUNCTIONS *~._
    
    ~* grammar_fuzz *~
    
    ~ Inputs ~
    subject: Our test subject, containing all relevant data. Defined in the Subject class.
    
    ~ Outputs ~
    txt. file containing 100,000 inputs that were fuzzed using the subject's grammar.
"""  
def grammar_fuzz(subject: Subject):
    subject_fuzzer = GrammarFuzzer(grammar=subject.grammar)
    for _ in range(0,100000):
        with open('results/' + subject.name + '/fuzzed_predictor.txt', 'a+') as file:
            file.write(f"{subject_fuzzer.fuzz()}\n")
    return


"""     
    ~* check_trigger *~
    
    ~ Inputs ~
    subject: Our test subject, containing all relevant data. Defined in the Subject class.
    inputs: List of inputs. Taken from a fuzzer directly or from an imported fuzzed file.
    
    ~ Outputs ~
    Dict sorted by lines. Each line entry contains the inputs that triggered it. 
    
    Runs input through an oracle set for the subject and the given line under test.  
"""  
def check_trigger(
    subject: Subject,
    inputs
):
    line_dict = {}
    
    for line in subject.relevant_lines:
        line_dict[str(line)] = []
        
        subject_oracle = construct_oracle(
            program_under_test=subject.first_func,
            inp_converter=subject.converter,
            line = line,
            resource_path=str(get_avicenna_rsc_path()),
            put_path=subject.put_path,
        )
        
        for input in inputs:
            if subject_oracle(input) == OracleResult.FAILING:
                line_dict[str(line)].append(input)
    
    return line_dict


"""     
    ~* ground_truth *~
    
    ~ Inputs ~
    subject: Our test subject, containing all relevant data. Defined in the Subject class.
    inputs: List of inputs. Taken from a fuzzer directly or from an imported fuzzed file.
    
    ~ Outputs ~
    File containing all inputs that triggered a given line. Saved as intermediary file, serves as ground truth for later predictor results.
    
    Instruments our program under test, checks for each input what lines it triggers in the subject and returns our results as a file.
"""  
def ground_truth(subject: Subject, inputs,):
    instrument(
        put_path=subject.put_path,
        instr_path=str(get_avicenna_rsc_path()) + '/instrumented.py',
    )
        
    result_dict = check_trigger(
                    subject=subject,
                    inputs=inputs,
                )
    
    for line in subject.relevant_lines:
        
        with open('results/' + subject.name + '/' + str(line) + '_line_triggered_fuzz.txt', 'w') as file:
            for item in result_dict:
                if str(item) == str(line):
                    for value in result_dict[item]:
                        file.write(f"{value}\n")