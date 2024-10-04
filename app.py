import os
import requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def update_exchange_rates(update_from, update_to):
    # Fetch exchange rates from National Bank of Ukraine API
    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json&date={update_from.strftime('%Y%m%d')}"
    response = requests.get(url)
    rates = response.json()

    # Process and format the data
    formatted_rates = []
    for rate in rates:
        formatted_rates.append([
            rate['exchangedate'],
            rate['cc'],
            rate['rate']
        ])

    # These are the IDs of the spreadsheet, and the one individual sheet in it to receive updated data from the bank
    # Unfortunately, only works with Google Sheet native spreadsheet format, does not work on .xslx :/
    SPREADSHEET_ID = '1AtLXJdjEwevQ-RPCtzv03qeVJ95m7Dh05IUAsPbfOQw'
    RANGE_NAME = 'solution!A1:C'

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    body = {
        'values': formatted_rates
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    
    print(f"{result.get('updatedCells')} cells updated.")

if __name__ == '__main__':
    # Set default dates if not provided
    update_from = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    update_to = update_from + timedelta(days=7)

    update_exchange_rates(update_from, update_to)