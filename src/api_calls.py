import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Suppress only the single warning from urllib3 needed.
import json
import yaml
import time
import sys
import logging
from logging import getLogger
import src
import datetime
import threading
from src import parse
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread #TODO add to reqruirments txt and install

logger = getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.addHandler(handler)

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
  cls.stories_list = list()
  
     
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
  print(f"Starting to retrieve all saved stories bases on hashes")
  print("Method 'get_all_starred_hashes' started")
  start_time = time.time()
  self.hashes=self.get_saved_stories_hashes(self.hashes)
  end_time = time.time() # End timing
  elapsed_time = end_time - start_time
  print(f"Method 'get_all_starred_hashes' took {end_time - start_time} seconds to run.")
  print(f"Running 'get_feeds'")
  time.sleep(self.sleeper) # Sleep to respect rate limit
  self.get_feeds()
  print(f"'get_feeds' execution finished")
  self.stories_list = self.get_starred_stories_by_hashes(self.hashes)
  end_time = time.time()
  print(f"'get_saved_stories' :: Retrieved {len(self.stories_list)} stories from NewsBlur")
  print(f"Total time taken to retrieve all saved stories and hashes: {end_time - start_time} seconds")
  print(f"Parsing stories with Content_Parser")
  parsed_stories = self.parser_object.parse_stories(self.stories_list)
  print(f"Validating parsed stories")
  print(f"//////////////////////////////////////////////////////////////////////")
  for item in parsed_stories:
    if 'origin' not in item or item['origin'] is None:
      try:
        print(f" ERROR:: Story {item['title']} has no origin. Setting to 'Unknown'")
      except KeyError as e:
        print(f" ERROR:: KeyError: {e} - Story item may not have a 'title' key.")
        print(f" ERROR:: <!!!> Story item: {item} has no title/origin/link field") #debug printout
      # item['origin'] = 'Unknown'
    else:
      print(f"Story {item['title']} has origin: {item['origin']}")
  print(f"//////////////////////////////////////////////////////////////////////")
  print(f"Validating parsed stories ------ Done")

  self.parsed_stories_list = parsed_stories
  print(f"Finished parsing stories with Content_Parser")
  # print(f"comparing parsed stories: {self.parsed_stories_list==parsed_stories}")

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
   
  print(f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} :: All Saved stories Aggregated in: {end_time - start_time} seconds") 
  # print(f"Stories: {self.stories_list}") #disable
  # for item in self.stories_list:
  #   if 'origin' not in item or item['origin'] is None:
  #     try:
  #       print(f"Story {item['title']} has no origin. Setting to 'Unknown'")
  #     except KeyError as e:
  #       print(f"KeyError: {e} - Story item may not have a 'title' key. Setting origin to 'Unknown'")
  #       print(f" <!!!> Story item: {item} has no title/origin/link field") #debug printout
  #     # item['origin'] = 'Unknown'
  #   else:
  #     print(f"Story {item['title']} has origin: {item['origin']}")
  print("Total stories saved to date: " +str(datetime.datetime.now().strftime("%Y-%m-%d")) + " : " + str(len(self.stories_list)))
  print(f"Total number of stories retrieved: {len(self.stories_list)}")
  print(f"Total number of parsed stories : {len(self.parsed_stories_list)}")
  print(f"Returing from 'get_Saved_stories'")
  return self.parsed_stories_list
  # return self.stories_list

 def get_feeds(self):
      '''
      Retrieves all the subscribed Feeds
      '''
      url_extention =r'/reader/feeds'
      try:
          feeds = self.connection_session.get(self.config['URL'] + url_extention , verify=True)
          if feeds.status_code==200:
                print(f"'get_feeds' Status code is : {str(feeds.status_code)}")
                #print(f"'get_feeds' Content: {str(feeds.content)}")
                
                active_feeds = json.loads(feeds.content.decode('utf-8'))['feeds']
                self.feeds_dict = self.parser_object.parse_feeds(active_feeds)
                print(f"Returning feeds_dict with {len(self.feeds_dict)} feeds")
                return self.feeds_dict
          else:
                print(f"'get_feeds' Status code is : {str(feeds.status_code)}")
                print(f"'get_feeds' Content: {str(feeds.content)}")
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
            # print(f"Hashes: {hashes}") #don't print large lists
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            return hashes
    print(f"Returning hashes list object")
    return hashes
 

 def get_starred_stories_by_hashes(self, story_hashes: list) -> list:
   print(f"Starting to 'get_starred_stories_by_hashes' with {len(story_hashes)} hashes")
   all_retrieved_stories = []
   chunk_size = 100 # API allows up to 100 hashes at a time
   # Split the list of hashes into chunks
  
   for i in range(0, len(story_hashes), chunk_size):

    chunk = story_hashes[i:i + chunk_size]
    print(f"Processing chunk {int(i/chunk_size) + 1} of {int(len(story_hashes)/chunk_size) + (1 if len(story_hashes) % chunk_size > 0 else 0)} with {len(chunk)} hashes.")

    # Construct the query parameters for the current chunk
    params = []
    for h in chunk:
        params.append(f"h={h}")
    query_string = "&".join(params)

    # Construct the full URL
    url = f"{self.config['URL']}/reader/starred_stories?{query_string}"

    try:
      print(f"Sleeping for {self.sleeper} seconds to respect rate limit.")
      time.sleep(self.sleeper)   # Respect the rate limit
      print(f"Sending GET request to URL: {url}")
      response = self.connection_session.get(url, verify=True) # verify=True for SSL certificate verification
      response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

      stories_data = response.json()
      if stories_data and 'stories' in stories_data:
        retrieved_count = len(stories_data['stories'])
        print(f"Successfully retrieved {retrieved_count} stories for this chunk.")
        all_retrieved_stories.extend(stories_data['stories'])
      else:
        print(f"No 'stories' key found in response for chunk starting with {chunk[0] if chunk else 'N/A'}.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code} Response: {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"Failed to decode JSON response: {json_err} - Content: {response.text}")
    
    # if (int(i/chunk_size) + 1) ==20:
    #     print(f"breaking the loop @ {int(i/chunk_size) + 1}:::'get_starred_stories_by_hashes':: Returning all rtrieved stories with total count: {len(all_retrieved_stories)}")
    #     return all_retrieved_stories
    #     break
  
   print(f"'get_starred_stories_by_hashes':: Returning all rtrieved stories with total count: {len(all_retrieved_stories)}")
   return all_retrieved_stories
 
 @classmethod
 def teardown(cls):
  '''
  Best practices
  '''
