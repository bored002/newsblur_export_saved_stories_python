import time
import sys
from src import api_calls
from src import data_parser
from src import data_processor
from src import email_client
def test_module():
    print("This is a Test.")
    print("waiting...")
    timer = 30
    while timer>0:
        print('Wait Time left : ' + str(timer))
        time.sleep(10)
        timer-=10        
    print("Done waiting.")
	
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
    if newsblur_object.login_newsblur() == True:
      data_parser_object  = data_parser.Data_Parser() 
      data_sciences = data_processor.data_science()
      saved_stories_dataframe = data_parser_object.convert_to_dataframe(newsblur_object.get_saved_stories())
      aggregation_dataframe = data_sciences.get_origin_distribution(saved_stories_dataframe)
      data_parser.Data_Parser.dataframe_to_csv(saved_stories_dataframe, 'saved_stories')
      data_parser.Data_Parser.dataframe_to_csv(aggregation_dataframe,'origin_distribution_aggregation','origin')

    #   emailer = email_client.Emailer()
    #   mail_sender = emailer.email_csv(stories_csv)
#   test_module()
 #Place Holder  to mark EOF
