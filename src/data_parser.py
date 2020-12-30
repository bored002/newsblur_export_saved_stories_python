import json
import logging

config_path = "config.yaml" 

class Story_Parser(object):
  @classmethod
  def __init__(cls):
    '''
    Place Holder
    '''
    cls.feed_dict = dict()
 
  def parse_stories(self, story_list):
    '''
    Parse stories froma pulled page 
    from each story exctract the following:
    1. Origin : [Lifehacker]
    2. Title: 
    3. Date
    4. Link to story

    each story will be a dict : {origin: , title, link, date , tags}
    '''
  
  def parse_feeds(self,feeds):
      '''
      Parsing Feeds matching ID and name
      '''
      for feed_id in feeds.keys():
          self.feed_dict[feed_id] = json.loads(feeds.content.decode('utf-8'))['feeds'][feed_id]['feed_title']
      return self.feed_dict
    
  @classmethod
  def teardown(cls):
    '''
    Best practice
    '''
