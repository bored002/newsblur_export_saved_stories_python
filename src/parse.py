import json
import logging
from logging import getLogger
from os.path import abspath
import pandas
from collections import OrderedDict
import time
import re
import datetime
import sys
import os
import inspect
config_path = "config.yaml" 

logger = getLogger(__name__)


class Content_Parser(object):
      
  @classmethod
  def __init__(cls):
    '''
    Initialize class
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
    # print("Parsing Story List") #debug
    for story in story_list:
      story_object = OrderedDict()
      # print("=======================================================") #debug
      # print(f"parse_stories::Parsing story: {story}") #debug
      # print(f"Story keys: {story.keys()}") #debug
      # print("=======================================================") #debug
      try:
        # print(f"Parsing story by 'story_feed_id'") #debug
        story_object['origin'] = self.feed_dict[str(story['story_feed_id'])]
        # print(f"'story_feed_id' :setting: Origin found: {story_object['origin']}") #debug
      except KeyError as e:
        print(f"KeyError: {e} - 'story_feed_id' not found in feed_dict") #debug        print(f"Origin not found in feed_dict, extracting from URL")
        print(f"using 'extract_origin_from_url' to find origin") #debug
        story_object['origin'] = self.extract_origin_from_url(story)

      story_object['title'] = story['story_title']
      if 'http' in story['id']:
        story_object['link'] = story['id']
      else:
            story_object['link'] =story['story_permalink']
      story_object['tags'] = story['story_tags']
      story_object['date'] = story['starred_date'] #TODO: Remove Yesterday/Today
      
      # print(f"Story Parsed: Adding to list: {story_object['title']} with {story_object['origin']}; full object {story_object}") #debug
      story_object_list.append(story_object)
    print(f"'parse_stories' :: Total stories parsed: {len(story_object_list)}")
    # for story in story_object_list:
    #   print("******************************************************************************")
    #   print(f"Story: {story['title']} - Origin: {story['origin']} - Link: {story['link']}")
    #   print("******************************************************************************")
    return story_object_list
  
  def extract_origin_from_url(self, story):
        '''
        In case there is no specific origin the origin will be extraced from the link URL
        '''
        print("Extracting origin from URL") #debug
        url = story['id']
        try:
          print(f"Extracting domain name from story ID: {story['id']}") #debug
          domain_name = story['id'].split("//")[1].split("/")[0].split(".")[0].lower()
          print(f"Extracted domain name: {domain_name}") #debug
        except IndexError:
          print(f"Failed to extract domain name from story ID: {story['id']}") #debug
          print(f"Using permalink to extract domain name") #debug
          domain_name = story['story_permalink'].split("//")[1].split("/")[0].split(".")[0].lower()
          print(f"Extracted domain name from permalink: {domain_name}") #debug
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
    print(f"Converting stories list to DataFrame with {len(stories_list)} stories") #debug
    self.stories_dataframe = pandas.DataFrame(stories_list)
    print(f"Stories DataFrame created with shape: {self.stories_dataframe.shape}") #debug
    print(f"Stories DataFrame columns: {self.stories_dataframe.columns.tolist()}") #debug
    print(f"Stories DataFrame head: {self.stories_dataframe.head()}") #debug
    print(f"Stories DataFrame info: {self.stories_dataframe.info()}") #debug
    print(f"Stories DataFrame: {self.stories_dataframe}") #
    
    return self.stories_dataframe
  
  @staticmethod
  def update_markdown_dashboard(delta_stories, total_stories, duplicate_stories, origin_distribution_df=None):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    parent_dir = os.path.dirname(script_dir)
    print(f"Parent directory: {parent_dir}")
    md_filepath = os.path.join(parent_dir, "index.md")
    print(f"Markdown file path: {md_filepath}:: is file exists? {os.path.isfile(md_filepath)}")
 
    if not os.path.exists(md_filepath):
        print(f"Error: Markdown file not found at '{md_filepath}'")
        return
    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("update_markdown_dashboard :: inputs:", {'delta_stories': delta_stories, 'total_stories': total_stories, 'duplicate_stories': duplicate_stories, 'timestamp': timestamp})
        
        # --- CORRECTED REGEX PATTERNS ---
        # The '\d*' now matches zero or more digits, so it will work even if the numbers are missing.
        content = re.sub(r'(- Delta of Stories:\s*)\d*', r'\g<1>' + str(delta_stories), content)
        content = re.sub(r'(- Total Count of Stories:\s*)\d*', r'\g<1>' + str(total_stories), content)
        content = re.sub(r'(- Duplicate Stories Count:\s*)\d*', r'\g<1>' + str(duplicate_stories), content)

        # Update or add a timestamp line
        timestamp_pattern = r'(- Last Updated: ).*'
        if re.search(timestamp_pattern, content):
            content = re.sub(timestamp_pattern, r'\g<1>' + timestamp, content)
        else:
            insert_point_pattern = r'(- Duplicate Stories Count:\s*\d*)'
            if re.search(insert_point_pattern, content):
                content = re.sub(insert_point_pattern, r'\g<1>\n- Last Updated: ' + timestamp, content)
            else:
                to_come_pattern = r'(- TO COME:)'
                if re.search(to_come_pattern, content):
                    content = re.sub(to_come_pattern, '- Last Updated: ' + timestamp + '\n\g<1>', content)
                else:
                    content += f"\n- Last Updated: {timestamp}\n"
        
        # --- NEW DEBUG PRINT STATEMENT ---
        print("\n--- Content to be written to file: ---")
        print(content)
        print("--------------------------------------\n")
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully updated numerical values in '{md_filepath}'")
        if origin_distribution_df is not None:
            df_markdown = origin_distribution_df.to_markdown(index=False)
            with open(md_filepath, 'a', encoding='utf-8') as f:
                f.write("\n\n## Saved Article Origin Distribution\n")
                f.write(df_markdown)
                f.write("\n")

            print(f"Successfully appended DataFrame to '{md_filepath}'")

    except Exception as e:
        print(f"An error occurred while updating the Markdown file: {e}")


  @staticmethod
  def dataframe_to_csv(data_frame, filename_prefix, index_column=False):
    '''
    Converts a pandas Data frame structure to a CSV format to send as email
    temporary solution
    '''
    absolute_path =(os.path.dirname(os.path.abspath(inspect.getabsfile(inspect.currentframe())))).replace('src','output')
    file_name = os.path.join(absolute_path,filename_prefix + "_" + str(time.strftime('%Y%m%d%H%M%S')) + ".csv")
    try:
      csv_file = data_frame.to_csv(file_name, encoding='utf-8', index=index_column) #df.to_csv(file_name, sep='\t', encoding='utf-8')
      if os.path.isfile(file_name):
        return csv_file
      else:
        print(f"Failed to generate file : {file_name}")
        return False
    except FileNotFoundError:
      print("Failed to convert to CSV.")
      return None

    
  @classmethod
  def teardown(cls):
    '''
    Best practice
    '''
