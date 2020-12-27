import requests
import json
import yaml
import logging

config_path = "config.yaml" 

class Newsblur_fetcher(object):
 
 @classmethod
 def __init__(cls, user_name, password):
  if user_name is None and password is None:
     with open(config_path) as ymlfile:
         cls.config = yaml.load(ymlfile)
  else:
     cls.config=dict()
     cls.config ={'user_name':user_name, 'password': password}
  cls.connection_session = requests.Session()
     
 def login(self):
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
   return('Response code is not 200')
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
        #TODO : Handle the stories better
        try:
          stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
        except requests.exceptions.RequestException as e:
          # logging.error("Loging API Call threw an exception: " + str(e))
          print(str(e))
        story_validation =self.validate_stories_page(stories_page)
        if story_validation!=True:
          print("Validation of stories page failed error: " + str(story_validation))
        
        # if stories_page.status_code!=200:
        #   print("Response code is not 200")
        #   return("Response code is not 200")
        # if json.loads(stories_page.content.decode('utf-8'))['stories'] is None:
        #   print("Page # " + str(page_index) + " returned no stories")
        #   return("Page # " + str(page_index) + " returned no stories")
        
        #stories_list.append(stories_page.content.decode('utf-8').replace("'", '"')['stories'])
        page_index+=1
  return stories_list

 def parse_stories(self, fresh_story_list):

  '''
  Parse stories froma pulled page 
  from each story exctract the following:
  1. Origin : [Lifehacker]
  2. Title: 
  3. Date
  4. Link to story

  each story will be a dict : {origin: , title, link, date , tags}
  #TODO : move this method to a separate module named parser
  '''

 def validate_stories_page(self, response):
  '''
  Validates that no errors were returned
  '''
  if response.status_code!=200:
          print("Response code is not 200")
          return("Response code is not 200")
  if json.loads(response.content.decode('utf-8'))['stories'] is None:
    print("Page # " + str(page_index) + " returned no stories")
    return("Page # " + str(page_index) + " returned no stories")
  return True
 
 #TODO parse the stories and write them to a good format for a file
   

if __name__ == "__main__":
  newsblur_object = Newsblur_fetcher()
  if newsblur_object.login() == True:
    x = newsblur_object.get_saved_stories()
