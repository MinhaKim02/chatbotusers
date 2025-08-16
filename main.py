from fastapi import FastAPI, Request, BackgroundTasks
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta
import os, requests
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


# --------------------------
# 카카오 API 키 불러오기
# --------------------------
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# --------------------------
# 카카오 장소 검색 함수
# --------------------------
def get_location_info(query: str):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": query}

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    if data.get("documents"):
        doc = data["documents"][0]
        return {
            "name": doc["place_name"],
            "address": doc.get("road_address_name") or doc.get("address_name"),
            "x": doc["x"],  # 경도
            "y": doc["y"]   # 위도
        }
    return None

# --------------------------
# Firestore 저장 함수
# --------------------------
def save_to_firestore(user_id: str, departure: str, arrival: str):
    dep_info = get_location_info(departure) if departure else None
    arr_info = get_location_info(arrival) if arrival else None

    data = {
        "departure": {
            "name": dep_info["name"] if dep_info else departure,
            "address": dep_info["address"] if dep_info else None,
            "x": dep_info["x"] if dep_info else None,
            "y": dep_info["y"] if dep_info else None,
        },
        "arrival": {
            "name": arr_info["name"] if arr_info else arrival,
            "address": arr_info["address"] if arr_info else None,
            "x": arr_info["x"] if arr_info else None,
            "y": arr_info["y"] if arr_info else None,
        },
        "updatedAt": datetime.now(timezone(timedelta(hours=9)))
    }

    db.collection("users").document(user_id).set(data, merge=True)

# --------------------------
# API 엔드포인트
# --------------------------
@app.post("/save_user_info")
async def save_user_info(req: Request, background_tasks: BackgroundTasks):
    body = await req.json()

    # 카카오톡에서 온 요청인지 확인
    if 'userRequest' in body:
        user_id = body['userRequest']['user']['id']
    else:  # 로컬 테스트
        user_id = body.get('userId', 'test-user')

    departure = body.get('action', {}).get('params', {}).get('departure', '')
    arrival = body.get('action', {}).get('params', {}).get('arrival', '')

    # Firestore 저장을 백그라운드에서 실행
    background_tasks.add_task(save_to_firestore, user_id, departure, arrival)

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": f"출발지: {departure}\n도착지: {arrival}\n(주소·좌표까지 저장 완료!)"
                    }
                }
            ]
        }
    }

@app.get("/")
async def root():
    return {"message": "Server is running!"}
