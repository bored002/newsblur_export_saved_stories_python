import json
import logging
import pandas
from collections import OrderedDict
import time
config_path = "config.yaml" 

class Data_Parser(object):
      
  @classmethod
  def __init__(cls):
    '''
    Place Holder
    '''
    cls.feed_dict = dict()
    cls.stories_dataframe = None
  def parse_stories(self, story_list):
    '''
    Parse stories froma pulled page 
    from each story exctract the following:
    each story will be a dict : {origin: , title, link, date , tags}
    '''
    
    story_object_list = list()
    # print("Parsing Story List")
    for story in story_list:
      story_object = OrderedDict()
      try:
        story_object['origin'] = self.feed_dict[str(story['story_feed_id'])]
      except KeyError:
        story_object['origin'] = self.extract_origin_from_url(story)
          # story_object['origin'] = 'Unknown'
      story_object['title'] = story['story_title']
      story_object['link'] = story['id']
      story_object['tags'] = story['story_tags']
      story_object['date'] = story['starred_date'] #TODO: Remove Yesterday/Today
      
      # print("Story Parsed: Adding to list")
      story_object_list.append(story_object)
    return story_object_list
  
  def extract_origin_from_url(self, story):
        '''
        In case there is no specific origin the origin will be extraced from the link URL
        '''
        url = story['id']
        try:
          domain_name = story['id'].split("//")[1].split("/")[0].split(".")[0].lower()
        except IndexError:
          domain_name = story['story_permalink'].split("//")[1].split("/")[0].split(".")[0].lower()
        for feed_name in self.feed_dict.values():
              if domain_name == feed_name.lower():
                    return feed_name
        return 'Unkown'

  
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
  
  def convert_to_dataframe(self, stories_list):
    '''
    Converts the list of stories (each story is a dict) to a dataframe object
    '''
    #TODO parse the stories and write them to a good format for a file
    # https://stackoverflow.com/questions/20638006/convert-list-of-dictionaries-to-a-pandas-dataframe
    self.stories_dataframe = pandas.DataFrame(stories_list)
    return self.stories_dataframe

  def data_frame_to_csv(self, data_frame):
    '''
    Converts a pandas Data frame structure to a CSV format to send as email
    temporary solution
    '''
    file_name = 'saved_stories'+"_" + str(time.strftime('%Y%m%d%H%M%S')) + ".csv"
    csv_file = pandas.DataFrame.to_csv(file_name, encoding='utf-8', index=False) #df.to_csv(file_name, sep='\t', encoding='utf-8')
    return csv_file

    
  @classmethod
  def teardown(cls):
    '''
    Best practice
    '''
