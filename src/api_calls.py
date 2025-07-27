import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Suppress only the single warning from urllib3 needed.
import json
import yaml
import time
import logging
import src
import datetime
import threading
from src import parse
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread #TODO add to reqruirments txt and install

config_path = "./configs/config.yaml" 
STARRED_HASHES_URL = "https://www.newsblur.com/reader/starred_story_hashes"
STARRED_STORIES_URL = "https://www.newsblur.com/reader/starred_stories"

class api_caller(object):
 
 @classmethod
 def __init__(cls, user_name, password):
  '''
  initialiaze class
  '''
  with open(config_path) as ymlfile:
      cls.config = yaml.load(ymlfile, Loader=yaml.FullLoader) #yaml.load(input, Loader=yaml.FullLoader)
  if user_name is not None and password is not None:
    cls.config['user_name'] = user_name
    cls.config['password'] = password
  cls.feeds_dict = dict()
  cls.parser_object = parse.Content_Parser()
  cls.connection_session = requests.Session()
  cls.hashes = []
  cls.rate_limit = 6
  cls.sleeper=15 # 10 Requests per minute
  
     
 def login_newsblur(self):
  '''
  performs a log-in action to initiate a session with the s
  '''
  extended_url = '/api/login'  
  payload = {'username': self.config['user_name'],'password' : self.config['password']}
  try:
      newblur_login = self.connection_session.post(self.config['URL']+extended_url, data=payload, verify=False)
  except requests.exceptions.RequestException as e:
   print(f"Request Exception in login {e}")
   return False
  if newblur_login.status_code!=200 or json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
   print("Authentication Failed.")
   print(f'Error Authentication Content:{str(newblur_login.content)}')
   print(f'Error: Authentication Response code is {str(newblur_login.status_code)}')
   return False
  print("Authentication: Succesfull")
  return True
  
 def get_saved_stories(self):
  '''
  Pulls all the saved stories page by page and returns an object with all the stories
  '''
  print(f"Testing Getting Hashes:")
  start_time = time.time
  self.hashes=self.get_saved_stories_hashes(self.hashes)
  end_time = time.time() # End timing
  print(f"end time {end_time}")
  # elapsed_time = end_time - start_time
  # print(f"Method 'get_all_starred_hashes' took {elapsed_time} seconds to run.")
  
  self.get_feeds()
  # print(f"Retrieved Feeds")
  # extended_url=r'/reader/starred_stories?page='
  # self.stories_list =list()
  # page_index = 1
  # print("Starting to read Saved Stories Feed.")
  # start_time =time.perf_counter()
  # try:
  #   print(f"First Call to get page from url {self.config['URL'] + extended_url+str(page_index)}")
  #   stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  # except requests.exceptions.RequestException as e:
  #   # logging.error("Loging API Call threw an exception: " + str(e))
  #   print(f"first api call caught requests exception: {e}")
  #   return False

  # stories_per_page = len(json.loads(stories_page.content.decode('utf-8'))['stories'])
  # # print(f"stories per page #1 : {stories_per_page}")
  
  # #TODO : improve to run asynch : Challenge
  # # while len(json.loads(stories_page.content.decode('utf-8'))['stories'])>0:
  # # while page_index<40:
  # while True:
  #       # print(f"Stories Count for page #{page_index}: {stories_per_page}")
  #       # print(f"len of stories: {len(json.loads(stories_page.content.decode('utf-8'))['stories'])>0}")
  #       # print("Page: " + str(page_index) + " Contains  : " + str(len(json.loads(stories_page.content.decode('utf-8'))['stories'])) + " stories.")
  #       try:
  #         # print(f"Sleeping: {self.sleeper}")
  #         time.sleep(self.sleeper)
  #         stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  #         if stories_page.status_code in [502, 429]:
  #          time.sleep(self.sleeper)
  #          # print(f"Waited sleeper period: {self.sleeper} due to server availability, buffered request")
  #          stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  #       except requests.exceptions.RequestException as e:
  #         print(f"Requests Exceptions {e}")
              
  #       story_validation =self.validate_stories_page(stories_page, page_index)
  #       if story_validation!=True:
  #         print("Validation of stories page failed error: " + str(story_validation))

  #       try:
          
  #         stories = json.loads(stories_page.content.decode('utf-8'))['stories']
  #         stories_per_page = len(stories)
  #         parsed_stories = self.parser_object.parse_stories(json.loads(stories_page.content.decode('utf-8'))['stories'])       
  #         self.stories_list.extend(parsed_stories)          
  #       except json.decoder.JSONDecodeError:
  #         pass        
  #       print(f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} :: Total stories retrieved and processed up to page index {page_index}: {len(self.stories_list)}") #debug printout
  #       if stories_per_page==0:
  #        print(f"No Stories were retrieved from page {page_index}. Breaking Retrieve loop")
  #        break
  #       page_index+=1
   
  print(f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} :: All Saved stories Aggregated in: {str(time.perf_counter()-start_time)} seconds") 
  # print(f"Stories: {self.stories_list}")
  # print("Total stories saved to date: " +str(datetime.datetime.now().strftime("%Y-%m-%d")) + " : " + str(len(self.stories_list)))
  return self.stories_list

 def get_feeds(self):
      '''
      Retrieves all the subscribed Feeds
      '''
      url_extention =r'/reader/feeds'
      try:
          feeds = self.connection_session.get(self.config['URL'] + url_extention , verify=True)
          if feeds.status_code==200:
                print(f"Status code is : {str(feeds.status_code)}")
                active_feeds = json.loads(feeds.content.decode('utf-8'))['feeds']
                self.feeds_dict = self.parser_object.parse_feeds(active_feeds)
                # return self.feeds_dict
          else:
                print(f"Status code is : {str(feeds.status_code)}")
                print(f"Content: {str(feeds.content)}")
                # return None
      except requests.exceptions.RequestException as e:
        # logging.error("Loging API Call threw an exception: " + str(e))
        print(f'Get Feeds: Caught requests exception: {str(e)}')
        # return None      
         
 def validate_stories_page(self, response, index):
  '''
  Validates that no errors were returned
  '''
  if response.status_code!=200:
          print(f"Response code is not 200 . Actual Response Code is : {str(response.status_code)}")
          print(f"Response Headers: {str(response.headers)}")
          print(f"Response Content: {str(response.content)}")
          return False
          # return("Response code is not 200")
  # print(f"Headers: {response.headers}")
  try:
    if json.loads(response.content.decode('utf-8'))['stories'] is None:
      print(f"Page # {str(index)} returned no stories")
      return(f"Page # {str(index)} returned no stories")
    return True
  except Exception as e:
    print('Failed to validate json content in response.')
    
    return False
 
 def send_get_request(self, url, index):
    """
    Sends a GET request to the given URL and prints the index.

    Args:
        url: The URL to send the request to.
        index: The index of the request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Request {index}: Successful! Status code: {response.status_code}")
        #TODO validate status code and content; 
        #TODO push content into a list and after all agregation is done then work on the list
    except requests.exceptions.RequestException as e:
        print(f"Request {index}: Failed! Error: {e}")

 def get_saved_stories_hashes(self,hashes=[]):    
    response = self.connection_session.get(STARRED_HASHES_URL, verify=True)
    if response.status_code != 200:
        print(f"Failed to fetch starred story hashes. Status code: {response.status_code}")
        return hashes
    else:
        print(f"Successfully fetched starred story hashes. Status code: {response.status_code}")
        try:
            data = response.json()
            hashes.extend(data.get("starred_story_hashes", []))
            print(f"Initial hashes retrieved: {len(hashes)}")
            print(f"Hashes: {hashes}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            return hashes
    print(f"Returngin hashes object")
    return hashes

 def run_parallel_requests(self, urls, num_threads):
    """
    Sends GET requests to the given URLs in parallel using threads.

    Args:
        urls: A list of URLs to send requests to.
        num_threads: The number of threads to use.
    """
    threads = []
    for i, url in enumerate(urls):
        thread = threading.Thread(target=send_get_request, args=(url, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
 
 @classmethod
 def teardown(cls):
  '''
  Best practices
  '''
