import time
import sys
import os
import inspect
import pandas
from src import ml_models
from src import api_calls
from src import parse
from src import data_processor
from src import email_client

if __name__ == "__main__":

    print(f"Arguments count: {len(sys.argv)}") #debug
    # for i, arg in enumerate(sys.argv):
    #     print(f"Argument {i:>6}: {arg}") # should pass newsblur user,password and google api key #debug
    #     print(" user : "  + str(sys.argv[1])) #debug
    #     print(" pass : "  + str(sys.argv[2])) #debug        
    try:
        user_name = sys.argv[1]
        password = sys.argv[2]
    except IndexError:
        print("Encountered Index Error in passed system arguments")
        user_name =None
        password = None
    newsblur_object = api_calls.api_caller(user_name,password)
    if newsblur_object.login_newsblur() != True:
        print('API Authentication Failed.')
        sys.exit("API Authentication Failed. Terminating Execution.")
    list_of_csv = os.listdir('downloads')
    print('Content of downloads folder: ' + str(list_of_csv))
    for csv in list_of_csv:
        if 'saved_stories' in csv:
            path_to_stories_list = os.path.join('downloads',csv)
            break
    previous_saved = pandas.read_csv(path_to_stories_list)
    previous_number_of_stories = previous_saved.shape[0]
    print('Yesterday`s saved stories count:'+ str(previous_number_of_stories))
    ml_models.ML_modeling.setup_experiment(previous_number_of_stories) #experiment to see if will crash
    parser_object  = parse.Content_Parser()
    data_sciences = data_processor.data_science()
    saved_stories_dataframe = parser_object.convert_to_dataframe(newsblur_object.get_saved_stories())
    current_number_of_stories = saved_stories_dataframe.shape[0]
    print('Today`s saved stories count:'+ str(current_number_of_stories))
    print('Change (Delta) in story count is :' + str(current_number_of_stories-previous_number_of_stories))
    aggregation_dataframe = data_sciences.get_origin_distribution(saved_stories_dataframe)    
    #TODO: Add call to ML Module  with saved_stories_dataframe
    ml_models.ML_modeling.setup_experiment(saved_stories_dataframe)
    parse.Content_Parser().dataframe_to_csv(saved_stories_dataframe, 'saved_stories')
    parse.Content_Parser().dataframe_to_csv(aggregation_dataframe,'origin_distribution_aggregation','origin')

    #   emailer = email_client.Emailer()
    #   mail_sender = emailer.email_csv(stories_csv)

#Place Holder  to mark EOF
