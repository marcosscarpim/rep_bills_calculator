# Copyright (C) 2017 Motorola, Inc.
# All Rights Reserved.
#
# The contents of this file are Motorola Confidential Restricted (MCR).
# __author__ = "mscarpim"

from __future__ import print_function
import httplib2

from oauth2client.client import GoogleCredentials
from apiclient import discovery
from googleapiclient import errors


class SpreadsheetComm(object):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.file']
    CLIENT_SECRET_FILE = 'rep-bills-calculator-e298e2538d86.json'
    APPLICATION_NAME = 'DF-spreadsheet_comm'
    DISCOVERY_URL = ('https://sheets.googleapis.com/$discovery/rest?'
                     'version=v4')

    def __init__(self):
        credentials = GoogleCredentials.from_stream(SpreadsheetComm.CLIENT_SECRET_FILE)
        credentials = credentials.create_scoped(SpreadsheetComm.SCOPES)
        conn = credentials.authorize(httplib2.Http())

        self.service = discovery.build('sheets', 'v4', http=conn,
                                       discoveryServiceUrl=SpreadsheetComm.DISCOVERY_URL)

    # returns all rows from a sheet in range specified
    # params: - id : spreadsheet id to apply
    #         - name : name of the tab you want
    #         - range : range to get values (Ex.: A2:K)
    def getValuesInRange(self, id, name, range):
        rangeName = "'" + name + "'!" + range
        result = self.service.spreadsheets().values().get(
            spreadsheetId=id, range=rangeName).execute()

        values = result.get('values', [])

        return values

    # write to a whole column
    # params: - id : spreadsheet id to apply
    #         - name : name of the sheet tab
    #         - column : column to be written (Ex.: J)
    #         - value : value to be written
    #         - input_option: 'RAW' to not parse value and 'USER_ENTERED' to parse (use this to wirte link)
    def updateColumnInfo(self, id, name, column, values, input_option):
        range = "'" + name + "'!" + column
        value_input_option = input_option
        value_range_body = {
            "values": values
        }
        data = [
            {
                'majorDimension': 'COLUMNS',
                'range': range,
                'values': value_range_body
            }
        ]
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }

        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=id,
                                                                  body=body).execute()

        # we hope all has just gone right, because batchUpdate is asynchronous
        return True

    # write to a whole row
    # params: - id : spreadsheet id to apply
    #         - name : name of the sheet tab
    #         - column : column to be written (Ex.: J)
    #         - value : value to be written
    #         - input_option: 'RAW' to not parse value and 'USER_ENTERED' to parse (use this to write link)
    def updateRowInfo(self, id, name, column, values, input_option):
        range = "'" + name + "'!" + column
        value_input_option = input_option
        value_range_body = {
            "values": values
        }
        data = [
            {
                'majorDimension': 'ROWS',
                'range': range,
                'values': value_range_body
            }
        ]
        body = {
            'valueInputOption': value_input_option,
            'data': data
        }

        self.service.spreadsheets().values().batchUpdate(spreadsheetId=id, body=body).execute()

        # we hope all has just gone right, because batchUpdate is asynchronous
        return True
