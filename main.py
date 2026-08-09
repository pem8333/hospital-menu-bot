import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Request
import pytz

app = FastAPI()

# 1단계에서 복사해둔 '이번주' 탭의 CSV 웹 게시 URL을 아래에 넣습니다.
CSV_URL = "여기에_이번주_탭_CSV_웹게시_URL_입력"

@app.post("/menu")
async def kakao_skill(request: Request):
    try:
        # KST 기준 오늘 날짜 가져오기 (예: '2026-08-10')
        tz = pytz.timezone('Asia/Seoul')
        today_str = datetime.now(tz).strftime('%Y-%m-%d')
        
        # CSV 실시간 로드 및 파싱
        df = pd.read_csv(CSV_URL)
        df['날짜'] = df['날짜'].astype(str).str.strip()
        
        row = df[df['날짜'] == today_str]
        
        if not row.empty:
            menu_text = f"🍱 {today_str} 구내식당 식단\n\n{row.iloc[0]['메뉴']}"
        else:
            menu_text = f"ℹ️ {today_str} 식단 정보가 등록되지 않았습니다."
            
    except Exception as e:
        menu_text = "⚠️ 식단 데이터를 불러오지 못했습니다. 관리자에게 문의해주세요."

    # 카카오톡 스킬 응답 포맷
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": menu_text}}]
        }
    }
