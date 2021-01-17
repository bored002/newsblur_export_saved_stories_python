import time
import sys
from src import api_calls
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
        print(f"Argument {i:>6}: {arg}")
    newsblur_object = api_calls.api_caller(None,None)
    if newsblur_object.login_newsblur() == True:
      rss_feeds = newsblur_object.get_feeds()
      rss_saved_stories = newsblur_object.get_saved_stories()
    test_module()
 #Place Holder  to mark EOF
