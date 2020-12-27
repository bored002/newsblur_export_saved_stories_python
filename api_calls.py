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
  extended_url=r'/reader/starred_stories?page='
  stories_list =list()
  page_index = 1
  stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=True)
  while len(json.loads(stories_page.content.decode('utf-8'))['stories'])>0:
        #TODO : Handle the stories better
        stories_page=self.connection_session.get(self.config['URL'] + extended_url+str(page_index),verify=False)
        if stories_page.status_code!=200:
          return("Bad response")
        if stories_page.content.decode('utf-8').replace("'", '"')['stories'] is None:
          return("Page : " + str(page_index) + " returned no stories")
        stories_list.append(stories_page.content.decode('utf-8').replace("'", '"')['stories'])
        page_index+=1
  return stories_list
 
 #TODO parse the stories and write them to a good format for a file
   

if __name__ == "__main__":
  newsblur_object = Newsblur_fetcher()
  if newsblur_object.login() == True:
    x = newsblur_object.get_saved_stories()
