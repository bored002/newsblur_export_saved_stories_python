import time
import sys
from src import api_calls
from src import data_parser
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
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}") # should pass newsblur user,password and google api key
    newsblur_object = api_calls.api_caller(None,None)
    if newsblur_object.login_newsblur() == True:
      rss_feeds = newsblur_object.get_feeds()
      data_parser_object  = data_parser.Data_Parser() 
      #   saved_stories = newsblur_object.get_saved_stories() # returns aggregated list of stories
      saved_stories_dataframe = data_parser_object.convert_to_dataframe(newsblur_object.get_saved_stories())
      csv_file = data_parser_object.data_frame_to_csv(saved_stories_dataframe)
      emailer = email_client.Emailer()
      mail_sender = emailer.email_csv(csv_file)
#   test_module()
