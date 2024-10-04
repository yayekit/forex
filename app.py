# if some other provider is chosen instead of google sheets - delete token.json
PROVIDER = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1AtLXJdjEwevQ-RPCtzv03qeVJ95m7Dh05IUAsPbfOQw'
SHEET_NAME = 'forex'
API_FOREX_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import requests

app = Flask(__name__)

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, PROVIDER)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, PROVIDER)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def date_range(start_date, end_date):
	for n in range(int((end_date - start_date).days) + 1):
		yield start_date + timedelta(n)

def clear_spreadsheet():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    request = service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!A1:ZZ'
    )
    request.execute()

def update_exchange_rates(update_from, update_to):
	# comment the line below to write into the existing data
	clear_spreadsheet()

	data_by_date = {}
	currency_codes = set()

	for single_date in date_range(update_from, update_to):
		url = f"{API_FOREX_URL}?json&date={single_date.strftime('%Y%m%d')}"
		response = requests.get(url)
		rates = response.json()

		date_str = single_date.strftime("%Y-%m-%d")
		data_by_date[date_str] = {}

		for rate in rates:
			currency_code = rate['cc']
			currency_codes.add(currency_code)
			data_by_date[date_str][currency_code] = rate['rate']

	sorted_currency_codes = sorted(currency_codes)
	header_row = ['Date'] + sorted_currency_codes

	rows = []
	rows.append(header_row)
	for date_str in sorted(data_by_date.keys()):
		row = [date_str]
		for currency_code in sorted_currency_codes:
			rate = data_by_date[date_str].get(currency_code, '')
			row.append(rate)
		rows.append(row)

	creds = get_credentials()
	service = build('sheets', 'v4', credentials = creds)

	clear_request = service.spreadsheets().values().clear(
		spreadsheetId = SPREADSHEET_ID, range = SHEET_NAME)
	clear_request.execute()

	body = {
		'values': rows
	}
	result = service.spreadsheets().values().update(
		spreadsheetId = SPREADSHEET_ID, range = SHEET_NAME,
		valueInputOption = 'USER_ENTERED', body = body).execute()
	print("Rates updated successfully")

@app.route('/update_rates', methods=['GET'])
def api_update_rates():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'error': 'Both start_date and end_date are required'}), 400

    try:
        update_from = datetime.strptime(start_date, "%Y-%m-%d")
        update_to = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-D'}), 400

    if update_to < update_from:
        return jsonify({'error': 'end_date must be equal to or greater than start_date'}), 400

    try:
        update_exchange_rates(update_from, update_to)
        return jsonify({'message': 'Exchange rates updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
	# app.run(debug = True)
	pass
	# uncomment the below for local runs
	#
	# while True:
	# 	try:
	# 		update_from = datetime.strptime(input("Enter the *start* date for rate updates (YYYY-MM-DD): "), "%Y-%m-%d")
	# 		break
	# 	except ValueError:
	# 		print("Invalid date format! Please use YYYY-MM-DD.")

	# while True:
	# 	try:
	# 		update_to = datetime.strptime(input("Enter the *end* date for rate updates (YYYY-MM-DD): "), "%Y-%m-%d")
	# 		if update_to > update_from:
	# 			break
	# 		else:
	# 			print("The *end* date must be equal or greater than the *start* date!")
	# 	except ValueError:
	# 		print("Invalid date format! Please use YYYY-MM-DD.")

	# update_exchange_rates(update_from, update_to)