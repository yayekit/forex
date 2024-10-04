# Forex Rate Updater

This Python script fetches and updates Ukrainian hryvna foreign exchange rates from the National Bank of Ukraine, and writes them to a pre-defined Google Sheets document.

Works both on the Web, and locally.

## Web Access

Make a GET request to the following endpoint:
```
https://yayekit.pythonanywhere.com/update_rates?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```
, where `YYYY-MM-DD` is the desired start and end dates for the rates to be fetched.

### Google Sheets Integration

The fetched rates are written into the:
[Google Sheets document](https://docs.google.com/spreadsheets/d/1AtLXJdjEwevQ-RPCtzv03qeVJ95m7Dh05IUAsPbfOQw/edit?gid=650071953#gid=650071953)

**Important!**: Both the GET request and the locally run script clear the content of the Google Sheets spreadsheet before writing the new rates in! If you need to keep peviously fetched information intact, modify the `update_exchange_rates()` function in the `app.py` script.

## Local Execution

- The source code is in `app.py`
- Required files, that are not present in the repo, and have to be created manually by the user:
	- `credentials.json`: Google Sheets API credentials;
	- `token.json`: OAuth 2.0 token for Google Sheets API

### Configuration

To run the file locally:
1. Follow the inline comments at the end of `app.py` and uncomment the designated lines;
2. Modify the URLs/names in the beginning of `app.py` (if needed);
3. Execute `app.py`

### Dependencies

- Flask
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client

The dependencies are in the `requirements.txt` file. To install them:

```bash
pip install -r requirements.txt
```