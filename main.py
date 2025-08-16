from fastapi import FastAPI, Request, BackgroundTasks
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# .env 불러오기 (Render에서는 /etc/secrets/.env 위치)
load_dotenv("/etc/secrets/.env")

app = FastAPI()

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    key_path = os.getenv("FIREBASE_KEY_PATH")  # .env에서 읽어옴
    cred = credentials.Certificate(key_path)   # 파일 경로 전달
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Firestore 저장 로직 분리
def save_to_firestore(user_id: str, departure: str, arrival: str):
    doc_ref = db.collection("users").document(user_id)
    KST = timezone(timedelta(hours=9))
    doc_ref.set({
        "departure_text": departure,
        "arrival_text": arrival,
        "updatedAt": datetime.now(KST)
    }, merge=True)

@app.post("/save_user_info")
async def save_user_info(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()
    if 'userRequest' in body:  # 카카오 요청
        user_id = body['userRequest']['user']['id']
    else:  # 로컬 테스트
        user_id = body.get('userId', 'test-user')

    departure = body.get('action', {}).get('params', {}).get('departure', '')
    arrival = body.get('action', {}).get('params', {}).get('arrival', '')

    # 🔥 백그라운드에서 저장 처리 (응답은 미리 보냄)
    background_tasks.add_task(save_to_firestore, user_id, departure, arrival)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"출발지: {departure}\n도착지: {arrival} 저장 요청 완료!"
                    }
                }
            ]
        }
    }

@app.get("/")
async def root():
    return {"message": "Server is running!"}
