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
    print("🚀 클로바 OCR 처리 시작...")
    ocr_result = run_clova_ocr()
    fields = ocr_result.get('images', [{}])[0].get('fields', [])
    
    if not fields:
        print("⚠️ OCR에서 글자를 인식하지 못했습니다.")
        # 빈 데이터라도 업데이트하여 에러 방지
        update_google_sheet([['인식실패', '이미지를 다시 확인해주세요.']])
    else:
        # 1. OCR이 인식한 모든 글자 뽑아내기
        extracted_texts = [f['inferText'] for f in fields]
        full_text = " ".join(extracted_texts)
        print("✅ 추출된 텍스트 일부:", full_text[:50])

        # 2. 구글 시트에 저장할 형태로 만들기
        # 챗봇이 '오늘 날짜'로 검색하기 때문에, 2월 이미지 테스트 중이더라도
        # 날짜는 이번 주(8월 10일, 11일)로 강제로 맞춰서 테스트해 보겠습니다.
        menu_data = [
            ['2026-08-10', full_text],   # 월요일 날짜에 OCR 전체 결과 쑤셔넣기 테스트
            ['2026-08-11', '화요일 정상작동 확인']
        ] 
        
        update_google_sheet(menu_data)
        print("✅ '다음주' 탭 식단 업데이트 완료")
