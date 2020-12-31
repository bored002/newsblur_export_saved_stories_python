import json
import logging
import pandas

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
    each story will be a dict : {origin: , title, link, date , tags}
    '''
    
    story_object_list = list()
    print("Parsing Story List")
    for story in story_list:
      story_object = dict()
      try:
          story_object['origin'] = self.feed_dict[str(story['story_feed_id'])]
      except KeyError:
          story_object['origin'] = 'Unknown'
      story_object['title'] = story['story_title']
      story_object['link'] = story['id']
      story_object['date'] = story['starred_date'] #TODO: Remove Yesterday/Today
      story_object['tags'] = story['story_tags']
      print("Story Parsed: Adding to list")
      story_object_list.append(story_object)
    #  story_object = dict()
    return story_object_list
  
  def remove_duplicates(self, full_list):
    '''
    Removes duplicate stories from the list
    '''
    #TODO need to decide what is the duplicates criteria
  
  def parse_feeds(self,feeds):
      '''
      Parsing Feeds matching ID and name
      '''
      for feed_id in feeds.keys():
          self.feed_dict[feed_id] = feeds[feed_id]['feed_title']
      return self.feed_dict
  
  def build_dataframe(self, stories_list):
    '''
    Converts the list of stories (each story is a dict) to a dataframe object
    '''
    #TODO parse the stories and write them to a good format for a file
    # https://stackoverflow.com/questions/20638006/convert-list-of-dictionaries-to-a-pandas-dataframe
    stories_dataframe = pandas.DataFrame(stories_list)
    return stories_dataframe

    
  @classmethod
  def teardown(cls):
    '''
    Best practice
    '''
