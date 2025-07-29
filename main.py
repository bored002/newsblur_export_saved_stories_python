import time
import sys
import os
import inspect
import pandas
from src import api_calls
from src import parse
from src import data_processor
from src import email_client
import logging
from logging import getLogger, StreamHandler, Formatter

logger = getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.addHandler(handler)

print(f"Arguments count: {len(sys.argv)}")
print(f"Arguments: {sys.argv}")

if __name__ == "__main__":
#     print(f"Arguments count: {len(sys.argv)}") #debug
#     # for i, arg in enumerate(sys.argv):
#     #     print(f"Argument {i:>6}: {arg}") # should pass newsblur user,password and google api key #debug
#     #     print(" user : "  + str(sys.argv[1])) #debug
#     #     print(" pass : "  + str(sys.argv[2])) #debug        
    try:
        print(f"0 place arg : {sys.argv[1]}")
        user_name = sys.argv[1]
        password = sys.argv[2]
        logger.info(f"logger print: User/Password Parsed successfully.")
        print(f"User/Password Parssed sucesfully")
    except IndexError:
        print("Encountered Index Error in passed system arguments")
        user_name =None
        password = None
    newsblur_object = api_calls.api_caller(user_name,password)
    if newsblur_object.login_newsblur() != True:
        print('API Authentication Failed.',file=sys.stderr)
        sys.exit("API Authentication Failed. Terminating Execution.")
    print(f"Login - Passed")
    list_of_csv = os.listdir('downloads')
    print(f'Content of downloads folder: {list(list_of_csv)}',file=sys.stdout)
    path_to_stories_list = None
    for csv in list_of_csv:
        print(f'Checking if csv file is saved_stories csv')
        # if 'saved_stories' in csv and 'duplicated_saved_stories' not in csv:
        if csv.startswith('saved_stories'):
            path_to_stories_list = os.path.join('downloads',csv)
            print(f"path: {path_to_stories_list} found in downloads folder")
            break
    if path_to_stories_list:
        try:
            previous_saved = pandas.read_csv(path_to_stories_list)
            previous_number_of_stories = previous_saved.shape[0]
            # print(f'Previous Number of saved stories : {previous_number_of_stories}')
        except Exception as e:
            print(f"Pandas Exception Caught while reading previous saved stories: {e}")
            previous_number_of_stories = 0
    else:
        print(f"No saved stories were retrieved from the folder")
        print(f'No previous saved stories found, setting previous_number_of_stories to 0')
    # TODO: read from saved stories csv convert to dataframe and get length of list
    # TODO: Make sure when saving the stories we don't lose disonctinued feed
    
    try:
        parser_object  = parse.Content_Parser()
        data_sciences = data_processor.data_science()
        print(f'parser and data processor iniated')
        # stories = newsblur_object.get_saved_stories()
        # print(f'Number of stories retrieved from NewsBlur: {len(stories)}')
        print(f"Creating 'saved_stories_dataframe' from retrieved stories with inner calls")
        saved_stories_dataframe = parser_object.convert_to_dataframe(newsblur_object.get_saved_stories())
        current_number_of_stories = saved_stories_dataframe.shape[0]

        duplicateRowsDF = saved_stories_dataframe[saved_stories_dataframe.duplicated(['title'])]    
        print('==========================================================================')
        print(f'Previous Number of saved stories : {previous_number_of_stories}')
        print(f'Current saved stories count:{current_number_of_stories}')
        print(f'Change (Delta) in story count is :{current_number_of_stories-previous_number_of_stories}')
        print(f'get_origin_distribution calling')
        aggregation_dataframe = data_sciences.get_origin_distribution(saved_stories_dataframe)
        print(f'Converting saved stories dataframe to csv')
        parse.Content_Parser().dataframe_to_csv(saved_stories_dataframe, 'saved_stories')
        print(f'Converting aggregation dataframe to csv')
        parse.Content_Parser().dataframe_to_csv(aggregation_dataframe,'origin_distribution_aggregation','origin')
        print(f'Converting dataframes to CSV completed')
        print(f'Content of output folder: {os.listdir("output")}')
        parse.Content_Parser().dataframe_to_csv(duplicateRowsDF, 'duplicated_saved_stories') 
        print(f"Count of duplicate stories: {duplicateRowsDF.shape[0]}")
        print('==========================================================================')
        print("Duplicate values based on a story title column are:", duplicateRowsDF, sep='\n')
        print('==========================================================================')
        print(f'Updating markdown dashboard with delta stories, total stories and duplicate stories :: Test')
        parse.Content_Parser().update_markdown_dashboard((current_number_of_stories-previous_number_of_stories), current_number_of_stories, duplicateRowsDF.shape[0]) #update_markdown_dashboard(delta_stories, total_stories, duplicate_stories)
    except Exception as general_e:
        print(f"Exception Caught: {general_e}")
    print()
    #TODO:
    # Add plot for : network graph --> stories saved by feed
    # Add plot/widget for Delta of stories saved, total stories, stories by feed
    # Add plot/widget for Sankey Diagram
    
    #   emailer = email_client.Emailer()
    #   mail_sender = emailer.email_csv(stories_csv)

#Place Holder  to mark EOF