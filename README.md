# 📢 chatbotusers

종로구 집회 알림 챗봇의 사용자 정보를 관리하는 프로젝트입니다.
카카오톡 챗봇(FastAPI 연동)에서 입력받은 **출발지/도착지, 좌표 등 사용자 정보**를 DB에 저장하고,
사용자의 출퇴근 경로와 집회 정보를 비교해 알림을 제공하는 데 활용됩니다.

---

## 🚀 기술 스택

* Python 3.8+ (개발 환경: Python 3.9)
* FastAPI
* Firebase Firestore
* Uvicorn
* python-dotenv

---

## 📦 설치 및 실행 방법

```bash
# 1. 레포 클론
git clone https://github.com/MinhaKim02/chatbotusers.git
cd chatbotusers

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔑 환경 변수 설정

`.env` 파일을 생성하고 Firebase 키 경로를 지정합니다:

```ini
FIREBASE_KEY_PATH=/etc/secrets/firebase_key.json
```

---

## 📡 주요 API 엔드포인트

* `POST /register` → 사용자 출발지/도착지 저장
* `POST /today-protests` → 오늘 날짜 기준 집회 정보 조회
* `POST /route-check` → 사용자의 출퇴근 경로와 집회 겹치는지 판별

---

## 🗂️ 데이터 구조 예시 (Firestore)

```json
{
  "departure_text": "성신여대입구역",
  "arrival_text": "종각역",
  "departure_coords": [37.5926, 127.0167],
  "arrival_coords": [37.5700, 126.9820],
  "created_at": "2025-08-22T09:00:00+09:00"
}
```

---

## 📋 실행 결과 예시

```json
{
  "message": "오늘 출퇴근경로에 집회가 있습니다.",
  "route_distance_m": 4969,
  "nearby_events": [
    {
      "time": "14:00~17:00",
      "location": "서울역 광장",
      "participants": 1500
    }
  ]
}
```

---

## 🔮 앞으로 추가 예정 기능

* 사용자 알림톡 자동 발송 기능
* DB 마이그레이션 (Firestore → MySQL/Aiven 등)
* 관리자용 대시보드

민하님, 혹시 제가 `requirements.txt`까지 같이 만들어드릴까요?
