import gspread
from oauth2client.service_account import ServiceAccountCredentials


class google_sheets_itegration(object):

    @classmethod
    def __init__(cls):
        '''
        Constructor method.
        '''

    def push_to_google_sheet(self, data_frame, sheet_id):
        '''
            Pushing the Data Frame to a google sheet worksheet.
        '''
        #TODO:
        # 1. If an older backup sheet exists delete it 
        # 2. Generate a timestamp --> figure out where to add it 
        # 3. Write to a new sheet.
        ServiceAccountCredentials.from_json()

    def pull_from_google_sheet(self,sheet_id):
            '''
            Pulls latest backup sheet 
            '''
            #TODO possibly latest Trend page and the

    