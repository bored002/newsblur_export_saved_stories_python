import requests
import json

config_path = "config.yaml" 

class Newsblur_fetcher(object):
 
 @classmethod
 def __init__(cls):
    with open(config_path) as ymlfile:
        cls.config = yaml.load(ymlfile)
     
 def login(self):
  '''
  performs a log-in action to initiate a session with the s
  '''
  extended_url = '/api/login'  
  payload = {'username': self.config['user_name'],'password' : self.config['password'].encode('utf-8')}
  response = requests.post(self.config['URL']+extended_url, data=payload,verify=False)
  if response.status_code==200 and json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']==True:
   return True
  elif esponse.status_code!=200:
   return('Response code is not 200')
  elif json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['authenticated']!=True:
   return('Authentication Failed:'  + str(json.loads(newblur_login.content.decode('utf-8').replace("'", '"'))['errors']))

