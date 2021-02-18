import pandas
import seaborn
import matplotlib
import matplotlib.pyplot as plt
class data_science(object):
    '''
    This module will handle various data analysis actions

    '''

    @classmethod
    def __init__(cls):
        '''
        Initialize class
        '''

    def get_origin_distribution(self, raw_data_frame):
        '''
        Generates a Data Frame which conaints the story distribution per origin website (feed)
        '''
        grouped_data = raw_data_frame.groupby('origin').size() #TODO make sure the name of the columns are : Feed , Number of Saved Stories
        return grouped_data

    def update_distribution():
        '''
        '''

    def visualise_historgram(self,data_frame, indexs_list):
        '''
        Generates a histogram graph using from a data frame based on the provided indexes
        '''
        #TODO Add legends to be more interperative
        seaborn.displot(data_frame, binwidth = 3)
        plt.show()

    def analyze_trends():
        '''
        Analyze the trends for each feed:  +/- from last sample
        '''

    @classmethod
    def teardown_class(cls):
        '''
        Template
        '''
