#!/usr/bin/env python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pyspeedtest
import datetime
import time

SPEED_TEST_HOST_SERVER = "speedtest.usinternet.com:8080"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1PXujhhz-4NWpUHGqQ_D0pukY35jBWyBw7zgIOzBKp60'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

TEST_SPREADSHEET_ID = '1PXujhhz-4NWpUHGqQ_D0pukY35jBWyBw7zgIOzBKp60'
TEST_RANGE_NAME = 'Test Sheet!A:C'

CREDENTIALS_JSON_PATH = '/Users/forsythetony/Documents/Coding/python/speed_tester/credentials/speed_tester_creds.json'

MINUTES_BETWEEN_CALLS = .5

def convert_to_mbps(bitsPerSecond):

    mbs_per_second = bitsPerSecond / 1000000

    return mbs_per_second


def get_formatted_date_string():
    now = datetime.datetime.now()
    return str(now)


def get_network_results():    
    st = pyspeedtest.SpeedTest(SPEED_TEST_HOST_SERVER)

    ping = st.ping()

    download_speed = st.download()
    download_speed_mbps = convert_to_mbps(download_speed)

    upload_speed = st.upload()
    upload_speed_mbps = convert_to_mbps(upload_speed)

    results = []

    timestamp = get_formatted_date_string()
    results.append(timestamp)
    results.append(SPEED_TEST_HOST_SERVER)
    results.append(ping)
    results.append(download_speed_mbps)
    results.append(upload_speed_mbps)

    return results


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    while True:
        results = get_network_results()

        upload_results_using_service(service, results)

        print("Uploaded network results will now sleep for 5 seconds")
        
        time.sleep(5)
    

def upload_results_using_service(service, results):
    # Call the Sheets API
    resource = {
        "majorDimension": "ROWS",
        "values": [results]
    }

    service.spreadsheets().values().append(spreadsheetId=TEST_SPREADSHEET_ID,
                                                 range=TEST_RANGE_NAME,
                                                    body=resource,
                                                    valueInputOption='USER_ENTERED'
                                                    ).execute()
if __name__ == '__main__':
    main()