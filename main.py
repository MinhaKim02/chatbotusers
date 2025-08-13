# main.py
from fastapi import FastAPI, Request
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os, json

app = FastAPI()

# Firebase 연결: 환경변수에서 서비스 계정 키 읽기
cred_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"])
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.post("/save_user_info")
async def save_user_info(req: Request):
    body = await req.json()

    user_id = body['userRequest']['user']['id']
    departure = body['action']['params'].get('departure')
    arrival = body['action']['params'].get('arrival')

    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({
        "departure_text": departure,
        "arrival_text": arrival,
        "updatedAt": datetime.utcnow()
    }, merge=True)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"출발지: {departure}\n도착지: {arrival} 저장 완료!"
                    }
                }
            ]
        }
    }
