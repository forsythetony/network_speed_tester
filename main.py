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
import yaml

SPEED_TEST_HOST_SERVER = None

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = None
TARGET_RANGE = None

CREDENTIALS_JSON_PATH = None

MINUTES_BETWEEN_CALLS = None

def set_config(config):
    print("Extracting config values...")
    
    global SPEED_TEST_HOST_SERVER
    global SPREADSHEET_ID
    global TARGET_RANGE
    global MINUTES_BETWEEN_CALLS

    if 'spreadsheet' not in config: 
        raise Exception("Missing 'spreadsheet' key in config")

    if 'id' not in config['spreadsheet']:
        raise Exception("Missing 'spreadsheet->id' key in config")
    
    if 'range' not in config['spreadsheet']:
        raise Exeption("Missing 'spreadsheet->range' key in config")

    SPREADSHEET_ID = config['spreadsheet']['id']
    TARGET_RANGE = config['spreadsheet']['range']

    if 'speed_server' in config:
        SPEED_TEST_HOST_SERVER = config['speed_server']
    else:
        SPEED_TEST_HOST_SERVER = 'speedtest.usinternet.com:8080'

    if 'minutes_between_calls' in config:
        MINUTES_BETWEEN_CALLS = config['minutes_between_calls']
    else:
        MINUTES_BETWEEN_CALLS = 60
    
    print("""\nConfig values:
    Spreadsheet ID:\t{}
    Spreadsheet Range:\t{}
    Speed Test Server:\t{}
    Minutes Between Calls:\t{}
    """.format(
        SPREADSHEET_ID, 
        TARGET_RANGE, 
        SPEED_TEST_HOST_SERVER, 
        MINUTES_BETWEEN_CALLS))
    
def load_config():

    script_dir = os.path.dirname(os.path.realpath(__file__))
    full_config_path = os.path.join(script_dir, 'config', 'config.yml')

    if not os.path.exists(full_config_path):
        raise Exception("Missing application config file at path -> {}".format(full_config_path))
    
    with open(full_config_path, 'r') as stream:
        try:
            set_config(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print("Failed to load the YAML file...")
            print(exc)
            raise Exception('Failed to open YAML file')

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
    """
    Load config from .yml file at 'config/config.yml'
    """
    load_config()

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

        seconds_between_calls = MINUTES_BETWEEN_CALLS * 60

        build_log_statement(MINUTES_BETWEEN_CALLS, results)
        
        time.sleep(seconds_between_calls)
    

def get_current_timestamp():
    now = datetime.datetime.now()
    return now.strftime('%m-%d-%y %H:%M:%S')

def build_log_statement(sleep_minutes, results):
    log_string = "[{}]".format(get_current_timestamp())
    log_string += "Test Results -> {}".format(results)
    log_string += "..."
    log_string += "Will now sleep for {} minutes".format(sleep_minutes)
    print(log_string)

def upload_results_using_service(service, results):
    # Call the Sheets API
    resource = {
        "majorDimension": "ROWS",
        "values": [results]
    }

    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID,
                                                 range=TARGET_RANGE,
                                                    body=resource,
                                                    valueInputOption='USER_ENTERED'
                                                    ).execute()

if __name__ == '__main__':
    main()
