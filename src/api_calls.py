# import src
import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # Suppress only the single warning from urllib3 needed.
import json
import yaml
# import gspread #TODO add to reqruirments txt and install
import time
import logging
import src
import datetime
# try:

# except ModuleNotFoundError:
from src import parse
# from oauth2client.service_account import ServiceAccountCredentials

config_path = "./configs/config.yaml" 

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
  
     
 def login_newsblur(self):
  '''
  performs a log-in action to initiate a session with the s
  '''
  extended_url = '/api/login'  
  payload = {'username': self.config['user_name'],'password' : self.config['password']}
  try:
      newblur_login = self.connection_session.post(self.config['URL']+extended_url, data=payload,verify=False)
  except requests.exceptions.RequestException as e:
#    logging.error("Loging API Call threw an exception: " + str(e))
   print(str(e))
   return False
  
  # if newblur_login.status_code==200 and json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']==True:
  #  print("Authentication: Succesfull")
  #  return True
  if newblur_login.status_code!=200 or json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
   print("Authentication Failed.")
   print('Error Content:' + str(newblur_login.content))
   print('Error: Response code is ' + str(newblur_login.status_code))
   return False
  # elif json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
  #  print('Authentication Failed:'  + str(json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['errors']))
  #  return False
  print("Authentication: Succesfull")
  return True
  
 def get_saved_stories(self):
  '''
  Pulls all the saved stories page by page and returns an object with all the stories
  '''
  self.get_feeds()
  extended_url=r'/reader/starred_stories?page='
  self.stories_list =list()
  page_index = 1
  print("Starting to read Saved Stories Feed.")
  start_time =time.perf_counter()
  try:
    stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  except requests.exceptions.RequestException as e:
    # logging.error("Loging API Call threw an exception: " + str(e))
    print(str(e))
    return False
  #TODO : improve to run asynch : Challenge
  while len(json.loads(stories_page.content.decode('utf-8'))['stories'])>0:
        # print("Page: " + str(page_index) + " Contains  : " + str(len(json.loads(stories_page.content.decode('utf-8'))['stories'])) + " stories.")
        try:
          stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
        except requests.exceptions.RequestException as e:
          # logging.error("Loging API Call threw an exception: " + str(e))
          print(str(e))
        if stories_page.status_code==502: #handling timeout 502
              time.sleep(30)
              try:
                stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
              except requests.exceptions.RequestException as e:
                #  logging.error("Loging API Call threw an exception: " + str(e))
                print(str(e))
              
        story_validation =self.validate_stories_page(stories_page, page_index)
        if story_validation!=True:
          print("Validation of stories page failed error: " + str(story_validation))

        try:
          stories = json.loads(stories_page.content.decode('utf-8'))['stories']
          parsed_stories = self.parser_object.parse_stories(json.loads(stories_page.content.decode('utf-8'))['stories'])       
          self.stories_list.extend(parsed_stories)          
        except json.decoder.JSONDecodeError:
          pass        
        print("Total stories retrieved and processed : " + str(len(self.stories_list))) #debug printout
        page_index+=1
  print("All Saved stories Aggregated in : " +str(time.perf_counter()-start_time)+ " seconds")   
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
                print("Status code is : " + str(feeds.status_code))
                active_feeds = json.loads(feeds.content.decode('utf-8'))['feeds']
                self.feeds_dict = self.parser_object.parse_feeds(active_feeds)
                # return self.feeds_dict
          else:
                print("Status code is : " + str(feeds.status_code))
                print('Content: ' + str(feeds.content))
                # return None
      except requests.exceptions.RequestException as e:
        # logging.error("Loging API Call threw an exception: " + str(e))
        print(str(e))
        # return None      
         
 def validate_stories_page(self, response, index):
  '''
  Validates that no errors were returned
  '''
  if response.status_code!=200:
          print("Response code is not 200 . Actual Response Code is : " + str(response.status_code))
          return False
          # return("Response code is not 200")
  try:
    if json.loads(response.content.decode('utf-8'))['stories'] is None:
      print("Page # " + str(index) + " returned no stories")
      return("Page # " + str(index) + " returned no stories")
    return True
  except Exception as e:
    print('Failed to validate json content in response.')
    print('Caught exception: ' + str(e))
    return False
 
 @classmethod
 def teardown(cls):
  '''
  Best practices
  '''

