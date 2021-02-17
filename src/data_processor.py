import pandas
import seaborn
import matplotlib

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
        grouped_data = raw_data_frame.groupby('origin').size()
        return grouped_data

    def update_distribution():
        '''
        '''

    def analyze_trends():
        '''
        Analyze the trends for each feed:  +/- from last sample
        '''

    @classmethod
    def teardown_class(cls):
        '''
        Template
        '''
