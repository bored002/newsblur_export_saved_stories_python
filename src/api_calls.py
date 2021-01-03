# import src
import requests
from urllib3.exceptions import InsecureRequestWarning
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
import json
import yaml
import logging
try:
  import data_parser # if executing just this script use this line
except ModuleNotFoundError:
  from src import data_parser # if executing main.py use this line

config_path = "./configs/config.yaml" 

class api_caller(object):
 
 @classmethod
 def __init__(cls, user_name, password):
  '''
  initialiaze class
  '''
  with open(config_path) as ymlfile:
      cls.config = yaml.load(ymlfile)
  if user_name is not None and password is not None:
    cls.config['user_name'] = user_name
    cls.config['password'] = password
  cls.parser_object = data_parser.Data_Parser()
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
  
  if newblur_login.status_code==200 and json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']==True:
   return True
  elif newblur_login.status_code!=200:
   return('Error: Response code is ' + str(newblur_login.status_code))
  elif json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
   return('Authentication Failed:'  + str(json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['errors']))
  
 def get_saved_stories(self):
  '''
  Pulls all the saved stories page by page and returns an object with all the stories
  '''
  extended_url=r'/reader/starred_stories?page='
  stories_list =list()
  page_index = 1
  
  try:
    stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  except requests.exceptions.RequestException as e:
    # logging.error("Loging API Call threw an exception: " + str(e))
    print(str(e))
    return False

  while len(json.loads(stories_page.content.decode('utf-8'))['stories'])>0:
        # print("Page: " + str(page_index) + " Contains  : " + str(len(json.loads(stories_page.content.decode('utf-8'))['stories'])) + " stories.")
        try:
          stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
        except requests.exceptions.RequestException as e:
          # logging.error("Loging API Call threw an exception: " + str(e))
          print(str(e))
        story_validation =self.validate_stories_page(stories_page, page_index)
        if story_validation!=True:
          print("Validation of stories page failed error: " + str(story_validation))
        stories = json.loads(stories_page.content.decode('utf-8'))['stories']
        parsed_stories = self.parser_object.parse_stories(json.loads(stories_page.content.decode('utf-8'))['stories'])       
        stories_list.extend(parsed_stories)
        print("Total stories retrieved and processed : " + str(len(stories_list)))
        page_index+=1
        
  return stories_list

 def get_feeds(self):
      '''
      Retrieves all the subscribed Feeds
      '''
      url_extention =r'/reader/feeds'
      try:
          feeds = self.connection_session.get(self.config['URL'] + url_extention , verify=True)
      except requests.exceptions.RequestException as e:
        # logging.error("Loging API Call threw an exception: " + str(e))
        print(str(e))
      if feeds.status_code!=200:
            print("Status code is : " + str(feeds.status_code))
      feeds_dict = dict()
      active_feeds = json.loads(feeds.content.decode('utf-8'))['feeds']
      feeds_dict = self.parser_object.parse_feeds(active_feeds)
      # json.loads(feeds.content.decode('utf-8'))['feeds']['6247287']['feed_title']
      return feeds_dict      

 def validate_stories_page(self, response, index):
  '''
  Validates that no errors were returned
  '''
  if response.status_code!=200:
          print("Response code is not 200")
          return("Response code is not 200")
  if json.loads(response.content.decode('utf-8'))['stories'] is None:
    print("Page # " + str(index) + " returned no stories")
    return("Page # " + str(index) + " returned no stories")
  return True
 
 @classmethod
 def teardown(cls):
  '''
  Best practices
  '''


if __name__ == "__main__":
  newsblur_object = api_caller(None,None)
  if newsblur_object.login_newsblur() == True:
    x = newsblur_object.get_feeds()
    y = newsblur_object.get_saved_stories()
