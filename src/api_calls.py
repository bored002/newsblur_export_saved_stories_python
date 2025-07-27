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
   logger.error(f"Request Exception in login {e}")
   return False
  if newblur_login.status_code!=200 or json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
   logger.error("Authentication Failed.")
   logger.error(f'Error Authentication Content:{str(newblur_login.content)}')
   logger.error(f'Error: Authentication Response code is {str(newblur_login.status_code)}')
   return False
  logger.info("Authentication: Succesfull")
  return True
  
 def get_saved_stories(self):
  '''
  Pulls all the saved stories page by page and returns an object with all the stories
  '''
  logger.info(f"Starting to retrieve all saved stories bases on hashes")
  start_time = time.time()
  self.hashes=self.get_saved_stories_hashes(self.hashes)
  end_time = time.time() # End timing
  elapsed_time = end_time - start_time
  logger.info(f"Method 'get_all_starred_hashes' took {end_time - start_time} seconds to run.")
  logger.info(f"Running 'get_feeds'")
  time.sleep(self.sleeper) # Sleep to respect rate limit
  self.get_feeds()
  logger.info(f"'get_feeds' execution finished")
  self.stories_list = self.get_starred_stories_by_hashes(self.hashes)
  end_time = time.time()
  # logger.info(f"Retrieved {len(self.stories_list)} stories from NewsBlur")
  # logger.info(f"Total time taken to retrieve all saved stories and hashes: {end_time - start_time} seconds")

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
   
  # print(f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} :: All Saved stories Aggregated in: {str(time.perf_counter()-start_time)} seconds") 
  # print(f"Stories: {self.stories_list}")
  # print("Total stories saved to date: " +str(datetime.datetime.now().strftime("%Y-%m-%d")) + " : " + str(len(self.stories_list)))
  logger.info(f"Total number of stories retrieved: {len(self.stories_list)}")
  return self.stories_list

 def get_feeds(self):
      '''
      Retrieves all the subscribed Feeds
      '''
      url_extention =r'/reader/feeds'
      try:
          feeds = self.connection_session.get(self.config['URL'] + url_extention , verify=True)
          if feeds.status_code==200:
                logger.info(f"'get_feeds' Status code is : {str(feeds.status_code)}")
                logger.info(f"'get_feeds' Content: {str(feeds.content)}")
                
                active_feeds = json.loads(feeds.content.decode('utf-8'))['feeds']
                self.feeds_dict = self.parser_object.parse_feeds(active_feeds)
                logger.info(f"Returning feeds_dict with {len(self.feeds_dict)} feeds")
                return self.feeds_dict
          else:
                logger.error(f"'get_feeds' Status code is : {str(feeds.status_code)}")
                logger.error(f"'get_feeds' Content: {str(feeds.content)}")
                # return None
      except requests.exceptions.RequestException as e:
        # logging.error("Loging API Call threw an exception: " + str(e))
        logger.info(f'Get Feeds: Caught requests exception: {str(e)}')
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
        logger.error(f"Failed to fetch starred story hashes. Status code: {response.status_code}")
        return hashes
    else:
        logger.info(f"Successfully fetched starred story hashes. Status code: {response.status_code}")
        try:
            data = response.json()
            hashes.extend(data.get("starred_story_hashes", []))
            logger.info(f"Initial hashes retrieved: {len(hashes)}")
            # print(f"Hashes: {hashes}") #don't print large lists
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return hashes
    logger.info(f"Returngin hashes object")
    return hashes
 

 def get_starred_stories_by_hashes(self, story_hashes: list) -> list:
   all_retrieved_stories = []
   chunk_size = 100 # API allows up to 100 hashes at a time

      # Split the list of hashes into chunks
   logger.info(f"Total number of hashes to process: {len(story_hashes)}")
   
  #  for i in range(0, len(story_hashes), chunk_size):
  #      if i == 1:
  #           logger.info(f"Skipping the first two hashes as per requirement.")
  #           break
  #      chunk = story_hashes[i:i + chunk_size]
  #      logger.info(f"Processing chunk {int(i/chunk_size) + 1} of {int(len(story_hashes)/chunk_size) + (1 if len(story_hashes) % chunk_size > 0 else 0)} with {len(chunk)} hashes.")


  #       # Construct the query parameters for the current chunk
  #      params = []
  #      for h in chunk:
  #          params.append(f"h={h}")
  #      query_string = "&".join(params)

  #       # Construct the full URL
  #      url = f"{self.config['URL']}/reader/starred_stories?{query_string}"

  #      try:
  #        logger.info(f"Sleeping for {self.sleeper} seconds to respect rate limit.")
  #        time.sleep(self.sleeper)   # Respect the rate limit
  #        logger.info(f"Sending GET request to URL: {url}")
  # #        response = self.connection_session.get(url, verify=True) # verify=True for SSL certificate verification
  # #        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

  # #        stories_data = response.json()
  # #        if stories_data and 'stories' in stories_data:
  # #         retrieved_count = len(stories_data['stories'])
  # #         logger.info(f"Successfully retrieved {retrieved_count} stories for this chunk.")
  # #         all_retrieved_stories.extend(stories_data['stories'])
  # #        else:
  # #           logger.warning(f"No 'stories' key found in response for chunk starting with {chunk[0] if chunk else 'N/A'}.")

  #     #  except requests.exceptions.HTTPError as http_err:
  #     #      logger.error(f"HTTP error occurred: {http_err} - Status Code: {response.status_code} Response: {response.text}")
  #      except requests.exceptions.ConnectionError as conn_err:
  #          logger.error(f"Connection error occurred: {conn_err}")
  #      except requests.exceptions.Timeout as timeout_err:
  #          logger.error(f"Timeout error occurred: {timeout_err}")
  #      except requests.exceptions.RequestException as req_err:
  #          logger.error(f"An unexpected error occurred: {req_err}")
  #     #  except json.JSONDecodeError as json_err:
  #     #      logger.error(f"Failed to decode JSON response: {json_err} - Content: {response.text}")
   logger.info(f"Total number of stories retrieved: {len(all_retrieved_stories)}")
   return all_retrieved_stories

#  def run_parallel_requests(self, urls, num_threads):
#     """
#     Sends GET requests to the given URLs in parallel using threads.

#     Args:
#         urls: A list of URLs to send requests to.
#         num_threads: The number of threads to use.
#     """
#     threads = []
#     for i, url in enumerate(urls):
#         thread = threading.Thread(target=send_get_request, args=(url, i))
#         threads.append(thread)
#         thread.start()

#     # Wait for all threads to finish
#     for thread in threads:
#         thread.join()
#    def send_get_request(self, url, index):
#     """
#     Sends a GET request to the given URL and prints the index.

#     Args:
#         url: The URL to send the request to.
#         index: The index of the request.
#     """
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for bad status codes
#         print(f"Request {index}: Successful! Status code: {response.status_code}")
#         #TODO validate status code and content; 
#         #TODO push content into a list and after all agregation is done then work on the list
#     except requests.exceptions.RequestException as e:
#         print(f"Request {index}: Failed! Error: {e}")

 
 @classmethod
 def teardown(cls):
  '''
  Best practices
  '''
