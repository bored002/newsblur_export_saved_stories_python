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
import networkx as nx # New import for creating graphs
import matplotlib.pyplot as plt # New import for plotting graphs

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
    for story in story_list:
      story_object = OrderedDict()
      try:
        story_object['origin'] = self.feed_dict[str(story['story_feed_id'])]
      except KeyError as e:
        print(f"KeyError: {e} - 'story_feed_id' not found in feed_dict")        
        print(f"Origin not found in feed_dict, extracting from URL")
        story_object['origin'] = self.extract_origin_from_url(story)

      story_object['title'] = story['story_title']
      if 'http' in story['id']:
        story_object['link'] = story['id']
      else:
            story_object['link'] =story['story_permalink']
      story_object['tags'] = story['story_tags']
      story_object['date'] = story['starred_date']
      
      story_object_list.append(story_object)
    print(f"'parse_stories' :: Total stories parsed: {len(story_object_list)}")
    return story_object_list
  
  def extract_origin_from_url(self, story):
        '''
        In case there is no specific origin the origin will be extraced from the link URL
        '''
        print("Extracting origin from URL")
        url = story['id']
        try:
          print(f"Extracting domain name from story ID: {story['id']}")
          domain_name = story['id'].split("//")[1].split("/")[0].split(".")[0].lower()
          print(f"Extracted domain name: {domain_name}")
        except IndexError:
          print(f"Failed to extract domain name from story ID: {story['id']}")
          print(f"Using permalink to extract domain name")
          domain_name = story['story_permalink'].split("//")[1].split("/")[0].split(".")[0].lower()
          print(f"Extracted domain name from permalink: {domain_name}")
        for feed_name in self.feed_dict.values():
              if domain_name == feed_name.lower():
                    return feed_name
        return 'Unkown'
  
  def remove_duplicates(self, full_list):
    '''
    Removes duplicate stories from the list
    '''
    pass
  
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
    print(f"Converting stories list to DataFrame with {len(stories_list)} stories")
    self.stories_dataframe = pandas.DataFrame(stories_list)
    print(f"Stories DataFrame created with shape: {self.stories_dataframe.shape}")
    print(f"Stories DataFrame columns: {self.stories_dataframe.columns.tolist()}")
    print(f"Stories DataFrame head: {self.stories_dataframe.head()}")
    print(f"Stories DataFrame info: {self.stories_dataframe.info()}")
    print(f"Stories DataFrame: {self.stories_dataframe}")
    
    return self.stories_dataframe
  
  @staticmethod
  def validate_markdown_file(md_filepath):
    '''
    Validates if the markdown file exists and is readable
    '''
    if not os.path.exists(md_filepath):
        print(f"Error: Markdown file not found at '{md_filepath}'")
        return False
    try:
        print("\n--- Verifying content by reading the file from disk... ---")
        with open(md_filepath, 'r', encoding='utf-8') as f_verify:
            verified_content = f_verify.read()
        
        print("\n" + verified_content)
        print("----------------------------------------------------------\n")
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return False
  
  @staticmethod
  def update_markdown_dashboard(delta_stories, total_stories, duplicate_stories, origin_distribution_df=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    md_filepath = os.path.join(parent_dir, "index.md")
    
    assets_dir = os.path.join(parent_dir, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    graph_image_path = os.path.join(assets_dir, "origin_network_graph.png")
    markdown_image_path = "assets/origin_network_graph.png"
 
    if not os.path.exists(md_filepath):
        print(f"Error: Markdown file not found at '{md_filepath}'")
        return
        
    try:
        updated_lines = []
        found_timestamp_line = False
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(md_filepath, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line.strip().startswith('- Delta of Stories'):
                    line = f"- Delta of Stories: {delta_stories}\n"
                elif line.strip().startswith('- Total Count of Stories'):
                    line = f"- Total Count of Stories: {total_stories}\n"
                elif line.strip().startswith('- Duplicate Stories Count'):
                    line = f"- Duplicate Stories Count: {duplicate_stories}\n"
                elif line.strip().startswith('- Last Updated:'):
                    line = f"- Last Updated: {timestamp}\n"
                    found_timestamp_line = True
                
                # The logic for graph generation is now updated for a Series
                elif origin_distribution_df is not None and line.strip() == '* Network Graph':
                    print("Attempting to create network graph for origin distribution...")
                    try:
                        if not isinstance(origin_distribution_df, pandas.Series):
                            raise TypeError("Expected pandas Series for origin distribution.")
                            
                        G = nx.Graph()
                        G.add_node("Saved Stories", size=2000, color='red')
                        
                        origin_counts = origin_distribution_df
                        total_count = origin_counts.sum()
                        
                        for origin, count in origin_counts.items():
                            node_size = 500 + (count / total_count) * 2000
                            G.add_node(origin, size=node_size)
                            G.add_edge("Saved Stories", origin)
                        
                        plt.figure(figsize=(10, 10))
                        pos = nx.spring_layout(G, k=0.5, iterations=50)
                        
                        node_sizes = [G.nodes[node]['size'] for node in G.nodes]
                        node_colors = ['red' if node == "Saved Stories" else 'skyblue' for node in G.nodes]
                        
                        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors)
                        nx.draw_networkx_edges(G, pos, edge_color='gray')
                        
                        labels = {node: f"{node}\n({origin_counts.get(node, '')})" for node in G.nodes}
                        labels["Saved Stories"] = "Saved Stories"
                        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
                        
                        plt.title("Saved Article Origin Network", size=16)
                        plt.axis('off')
                        plt.savefig(graph_image_path, bbox_inches='tight')
                        plt.close()
                        
                        line = f"![Saved Article Origin Distribution Network Graph]({markdown_image_path})\n"

                    except Exception as e:
                        print(f"Error generating network graph: {e}")
                        line = "\n"
                else:
                    updated_lines.append(line)
        
        content = "".join(updated_lines)

        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if origin_distribution_df is not None:
            # --- NEW: Convert the Series to a DataFrame before converting to Markdown ---
            df_for_markdown = origin_distribution_df.reset_index()
            df_for_markdown.columns = ['origin', 'count']
            
            df_markdown = df_for_markdown.to_markdown(index=False)
            with open(md_filepath, 'a', encoding='utf-8') as f:
                f.write("\n\n## Saved Article Origin Distribution\n")
                f.write(df_markdown)
                f.write("\n")
            print(f"Successfully appended DataFrame to '{md_filepath}'")

        print("\n--- Verifying final content by reading the file from disk... ---")
        with open(md_filepath, 'r', encoding='utf-8') as f_verify:
            verified_content = f_verify.read()
        print("\n" + verified_content)
        print("----------------------------------------------------------\n")
        
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
      csv_file = data_frame.to_csv(file_name, encoding='utf-8', index=index_column)
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
    pass
