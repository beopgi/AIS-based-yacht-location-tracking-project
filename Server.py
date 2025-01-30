# server.py
# flake8: noqa
import asyncio
import json
from fastapi import FastAPI, WebSocket
import websockets

# FastAPI 앱 생성
app = FastAPI()

# 메모리 내 데이터 저장 (MMSI 기준 최신 데이터 유지)
live_data = {}  # 실시간 위치 데이터 저장
live_data_lock = asyncio.Lock()  # 동시 접근 방지 Lock

# 항해 상태 코드 변환 함수
def get_navigational_status_text(status_code):
    status_texts = {
        0: "항해중(엔진사용)", 1: "정박 중", 2: "조종 불능", 3: "조종 제한",
        4: "흘수로 인한 조종 제한", 5: "계류 중", 6: "좌초됨", 7: "조업 중",
        8: "항해중(엔진사용X)", 9: "유해물질 운반중 1", 10: "유해물질 운반중 2",
        11: "뒤에서 견인", 12: "앞에서 견인", 13: "예약 상태", 14: "구조 요청",
        15: "할당되지 않음",
    }
    return status_texts.get(status_code, "Unknown")

# ✅ WebSocket 재연결을 위한 무한 루프
async def fetch_position_data():
    """
    AIS 실시간 위치(Position Report) 데이터를 지속적으로 수집하고 메모리에 저장.
    """
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "877c32d88cce08ea87119ba2736edcc0f6a6352d"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]  

    while True:  # 💡 끊어지면 자동 재연결을 위해 무한 루프 실행
        try:
            async with websockets.connect(url, ping_interval=30, ping_timeout=None) as websocket:
                await websocket.send(json.dumps({
                    "APIKey": api_key,
                    "BoundingBoxes": bounding_boxes,
                    "FiltersShipMMSI": [],
                    "FilterMessageTypes": ["PositionReport"],
                }))
                print("🟢 [실시간 위치 데이터] 구독 시작")

                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if "MessageType" not in data or data["MessageType"] != "PositionReport":
                        continue

                    ais_message = data["Message"]["PositionReport"]
                    meta_data = data["MetaData"]
                    mmsi = meta_data.get("MMSI", "Unknown")

                    async with live_data_lock:  # 💡 동시성 문제 방지
                        live_data[mmsi] = {
                            "mmsi": mmsi,
                            "name": meta_data.get("ShipName", "Unknown").strip(),
                            "latitude": ais_message["Latitude"],
                            "longitude": ais_message["Longitude"],
                            "cog": ais_message.get("Cog", 0.0),
                            "sog": ais_message.get("Sog", 0.0),
                            "true_heading": ais_message.get("TrueHeading", 0.0),
                            "navigational_status": get_navigational_status_text(ais_message.get("NavigationalStatus", "Unknown")),
                            "time_utc": meta_data.get("time_utc", "Unknown"),
                        }

                    print(f"🟢 [실시간 위치 데이터 수신] MMSI: {mmsi}, 위치: ({ais_message['Latitude']}, {ais_message['Longitude']})")

        except Exception as e:
            print(f"❌ [실시간 위치 데이터 오류] {e} | 5초 후 재연결 시도")
            await asyncio.sleep(5)  # 💡 재연결 시도 전에 5초 대기

# ✅ 서버 시작 시 데이터 수집 실행
@app.on_event("startup")
async def start_data_collection():
    asyncio.create_task(fetch_position_data())  

# ✅ WebSocket 엔드포인트: 실시간 데이터 전송
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # 클라이언트가 접속하면 현재 저장된 모든 데이터를 전송
    async with live_data_lock:  # 💡 동시 접근 방지
        await websocket.send_json(list(live_data.values()))
    print("📤 [초기 데이터 전송] 완료")

    try:
        while True:
            await asyncio.sleep(1)  
            async with live_data_lock:
                await websocket.send_json(list(live_data.values()))
            print("📤 [실시간 데이터 전송]")
    except Exception as e:
        print(f"❌ [WebSocket 연결 종료] {e}")

# ✅ REST API 엔드포인트: 현재 저장된 데이터 반환
@app.get("/ships")
async def get_all_ships():
    async with live_data_lock:
        return list(live_data.values())

# ✅ FastAPI 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
