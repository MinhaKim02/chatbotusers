from fastapi import FastAPI, Request, BackgroundTasks
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os, json

app = FastAPI()

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    cred_dict = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Firestore 저장 로직 분리
def save_to_firestore(user_id: str, departure: str, arrival: str):
    doc_ref = db.collection("users").document(user_id)
    doc_ref.set({
        "departure_text": departure,
        "arrival_text": arrival,
        "updatedAt": datetime.utcnow()
    }, merge=True)

@app.post("/save_user_info")
async def save_user_info(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()
    user_id = body['userRequest']['user']['id']
    departure = body['action']['params'].get('departure')
    arrival = body['action']['params'].get('arrival')

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
