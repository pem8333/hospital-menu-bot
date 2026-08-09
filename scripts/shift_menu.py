import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
GOOGLE_CREDENTIALS_JSON = os.environ['GOOGLE_CREDENTIALS']

def shift_menu():
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDENTIALS_JSON), scopes=['https://www.googleapis.com/auth/spreadsheets'])
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()

    # '다음주' 데이터 가져오기
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='다음주!A2:B100').execute()
    next_week_data = result.get('values', [])

    if next_week_data:
        # '이번주' 기존 데이터 지우고 덮어쓰기
        sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range='이번주!A2:B100').execute()
        sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='이번주!A2', valueInputOption='RAW', body={'values': next_week_data}).execute()
        print("✅ 월요일 자동 이관: '다음주' -> '이번주' 덮어쓰기 완료")

if __name__ == "__main__":
    shift_menu()
