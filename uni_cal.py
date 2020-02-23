from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from enum import IntEnum

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():    
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
    service = build('calendar', 'v3', credentials = creds)
    input_classes(service)

def populate_event(summary, location, start_date_time, end_date_time, until_date):
    return {'summary' : summary, 
    'location' : location, 
    'start' : {'dateTime' : start_date_time.isoformat(), 'timeZone' : 'Europe/Berlin'}, 
    'end' : {'dateTime' : end_date_time.isoformat(), 'timeZone' : 'Europe/Berlin'},
    'recurrence' : ['RRULE:FREQ=WEEKLY;UNTIL=' + until_date.isoformat().replace("-", "").replace(":","") + 'Z', 
        'EXDATE:' + holidays[0].isoformat().replace("-", "").replace(":","") + "Z" + "," + holidays[1].isoformat().replace("-", "").replace(":","") + 'Z']}

def input_classes(service):
    input_dict = {}
    break_condition = False
    while(break_condition == False):
        print("Which class?:")
        input_dict['summary'] = input()

        print("Where?:")
        input_dict['location'] = input()

        print("Which Day?:")
        input_dict['dayof'] = Day[input]

        print("Which DS?:")
        input_dict['ds'] = int(input())

        post_to_calendar(service, input_dict)

        print("Continue? (y/n):")
        user_input = input()
        if(user_input == "n"):
            break_condition = True
        
def post_to_calendar(service, input_dict):
    start_date = semester_calendar['start_first_half']
    weekday = next_weekday(start_date, input_dict['dayof'])
    start_time = create_date_from_ds(weekday, input_dict['ds'], True)
    end_time = create_date_from_ds(weekday, input_dict['ds'], False)
    event = populate_event(input_dict['summary'], input_dict['location'], start_time, end_time, semester_calendar['end_first_half'])
    service.events().insert(calendarId='primary', body=event).execute()
    print(event)
    start_date = semester_calendar['start_second_half']
    weekday = next_weekday(start_date, input_dict['dayof'])
    start_time = create_date_from_ds(weekday, input_dict['ds'], True)
    end_time = create_date_from_ds(weekday, input_dict['ds'], False)
    event = populate_event(input_dict['summary'], input_dict['location'], start_time, end_time, semester_calendar['end_second_half'])
    service.events().insert(calendarId='primary', body=event).execute()


ds_calendar = {
    1:{'start': {'hour': 7, 'minute':30}, 'end': {'hour': 9, 'minute':0}},
    2:{'start': {'hour': 9, 'minute':20}, 'end': {'hour': 10, 'minute':50}},
    3:{'start': {'hour': 11, 'minute':10}, 'end': {'hour': 12, 'minute':40}},
    4:{'start': {'hour': 13, 'minute':0}, 'end': {'hour': 14, 'minute':30}},
    5:{'start': {'hour': 14, 'minute':50}, 'end': {'hour': 16, 'minute':20}},
    6:{'start': {'hour': 16, 'minute':40}, 'end': {'hour': 18, 'minute':10}},
    7:{'start': {'hour': 18, 'minute':30}, 'end': {'hour': 20, 'minute':0}},
    8:{'start': {'hour': 20, 'minute':20}, 'end': {'hour': 21, 'minute':50}}
}

def next_weekday(dt, day):
    return dt + datetime.timedelta(days=((day-dt.weekday())%7))

def create_date_from_ds(date, ds, isStart):
    if(isStart == True):
        return date.replace(hour=ds_calendar[ds]['start']['hour'], minute=ds_calendar[ds]['start']['minute'])
    else:
        return date.replace(hour=ds_calendar[ds]['end']['hour'], minute=ds_calendar[ds]['end']['minute'])
    

semester_calendar = {
    'start_first_half': datetime.datetime(2019, 10, 14),
    'end_first_half': datetime.datetime(2019, 12, 21),
    'start_second_half': datetime.datetime(2020, 1, 6),
    'end_second_half': datetime.datetime(2020, 2, 8)
}

holidays = [
    datetime.datetime(2019, 10, 31),
    datetime.datetime(2019, 11, 20)
]

class Day(IntEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6
    
if __name__ == "__main__":
    main()