import requests

config_path = "config.yaml" 

class Newsblur_fetcher(object):
 
 @classmethod
 def __init__(cls):
    with open(config_path) as ymlfile:
        cls.config = yaml.load(ymlfile)

