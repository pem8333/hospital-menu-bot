import os
import json
import uuid
import time
import requests
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

CLOVA_API_URL = os.environ['CLOVA_API_URL']
CLOVA_SECRET_KEY = os.environ['CLOVA_SECRET_KEY']
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
GOOGLE_CREDENTIALS_JSON = os.environ['GOOGLE_CREDENTIALS']
IMAGE_PATH = 'data/menu.jpg'

def run_clova_ocr():
    with open(IMAGE_PATH, 'rb') as f:
        img_bytes = f.read()
    headers = {'X-OCR-SECRET': CLOVA_SECRET_KEY}
    payload = {'message': json.dumps({'images': [{'format': 'jpg', 'name': 'menu'}], 'requestId': str(uuid.uuid4()), 'version': 'V2', 'timestamp': int(round(time.time() * 1000))}).encode('UTF-8')}
    return requests.post(CLOVA_API_URL, headers=headers, data=payload, files=[('file', img_bytes)]).json()

def update_google_sheet(menu_list):
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_CREDENTIALS_JSON), scopes=['https://www.googleapis.com/auth/spreadsheets'])
    sheet = build('sheets', 'v4', credentials=creds).spreadsheets()
    
    # 기존 데이터 삭제 (A2부터) 후 새 데이터 덮어쓰기
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range='다음주!A2:B100').execute()
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range='다음주!A2', valueInputOption='RAW', body={'values': menu_list}).execute()

if __name__ == "__main__":
    ocr_result = run_clova_ocr()
    fields = ocr_result.get('images', [{}])[0].get('fields', [])
    
    # TODO: Template OCR을 사용하는 경우 반환되는 key(날짜)에 맞춰 데이터 구성 (현재는 예시 구조)
    # 아래는 임시 매핑이며, 실제 템플릿 필드명에 맞게 ['2026-08-10', 'A코너: ...'] 형태로 가공하셔야 합니다.
    menu_data = [
        ['2026-08-10', '월요일 메뉴 데이터 파싱 결과'], 
        ['2026-08-11', '화요일 메뉴 데이터 파싱 결과']
    ] 
    update_google_sheet(menu_data)
    print("✅ '다음주' 탭 식단 업데이트 완료")
