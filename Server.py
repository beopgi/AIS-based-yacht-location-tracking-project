# server.py
# flake8: noqa
import asyncio
import json
from fastapi import FastAPI, WebSocket
import websockets
from fastapi import WebSocketDisconnect

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

# 선박 타입 코드 변환 함수
def get_ship_type_text(a, b, c, d):
    length = a + b
    width = c + d

    if length <= 20 or width <=6:
        ship_type = "소형선박"
    elif 20 < length <= 50 and 6 < width <= 15:
        ship_type = "중형선박"
    else:
        ship_type = "대형선박"

    return ship_type

# 실시간 위치 데이터 수집
async def fetch_position_data():
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "1ce00146c35019a62bf6249802f5edd705cd8851"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]

    while True:
        try:
            async with websockets.connect(url) as websocket:
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
                  

                    async with live_data_lock:
                        if mmsi in live_data:
                            live_data[mmsi].update({
                                "latitude": ais_message["Latitude"],
                                "longitude": ais_message["Longitude"],
                                "cog": ais_message.get("Cog", 0.0),
                                "sog": ais_message.get("Sog", 0.0),
                                "true_heading": ais_message.get("TrueHeading", 0.0),
                                "name": meta_data.get("ShipName", "Unknown").strip(),
                                "navigational_status": get_navigational_status_text(ais_message.get("NavigationalStatus", "Unknown")),
                                "time_utc": meta_data.get("time_utc", "Unknown"),
                            })
                        else:
                            live_data[mmsi] = {
                                "mmsi": mmsi,
                                "latitude": ais_message["Latitude"],
                                "longitude": ais_message["Longitude"],
                                "cog": ais_message.get("Cog", 0.0),
                                "sog": ais_message.get("Sog", 0.0),
                                "true_heading": ais_message.get("TrueHeading", 0.0),
                                "name": meta_data.get("ShipName", "Unknown").strip(),
                                "navigational_status": get_navigational_status_text(ais_message.get("NavigationalStatus", "Unknown")),
                                "time_utc": meta_data.get("time_utc", "Unknown"),
                                "ship_type": "Unknown",
                            }
                    print(f"🟢 [실시간 위치 데이터 수신] MMSI: {mmsi}, 위치: ({ais_message['Latitude']}, {ais_message['Longitude']})")
        except Exception as e:
            print(f"❌ [실시간 위치 데이터 오류] {e} | 5초 후 재연결 시도")
            await asyncio.sleep(5)

# 선박 정적 데이터 수집
async def fetch_ship_static_data():
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "0fdc6251ffc2c7e5a2d74118769525f5012ef469"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]
    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps({
                    "APIKey": api_key,
                    "BoundingBoxes": bounding_boxes,
                    "FiltersShipMMSI": [],
                    "FilterMessageTypes": ["ShipStaticData"],
                }))
                print("🔵 [선박 정적 데이터] 구독 시작")

                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if "MessageType" not in data or data["MessageType"] != "ShipStaticData":
                        continue
                    ship_static_data = data["Message"]["ShipStaticData"]
                    Dimension = ship_static_data.get("Dimension", {})

                    DimensionA = Dimension.get("A", 0)
                    DimensionB = Dimension.get("B", 0)
                    DimensionC = Dimension.get("C", 0)
                    DimensionD = Dimension.get("D", 0)
                    ship_type = get_ship_type_text(DimensionA, DimensionB, DimensionC, DimensionD)

                    meta_data = data["MetaData"]
                    mmsi = meta_data.get("MMSI", "Unknown")

                    async with live_data_lock:
                        if mmsi in live_data:
                            live_data[mmsi]["ship_type"] = ship_type
                        else:
                            live_data[mmsi] = {
                                "mmsi": mmsi,
                                "latitude": "Unknown",
                                "longitude": "Unknown",
                                "cog": "Unknown",
                                "sog": "Unknown",
                                "true_heading": "Unknown",
                                "name": "Unknown",
                                "navigational_status": "Unknown",
                                "time_utc": "Unknown",
                                "ship_type": ship_type,
                            }
                    print(f"🔵 [선박 정적 데이터 수신] MMSI: {mmsi}, Type: {ship_type}")
        except Exception as e:
            print(f"❌ [선박 정적 데이터 오류] {e} | 5초 후 재연결 시도")
            await asyncio.sleep(5)

# 서버 시작 시 데이터 수집 실행
@app.on_event("startup")
async def start_data_collection():
    asyncio.create_task(fetch_position_data())
    asyncio.create_task(fetch_ship_static_data())

# WebSocket 엔드포인트 추가
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 [WebSocket 연결됨] 클라이언트가 접속했습니다.")

    try:
        while True:
            await asyncio.sleep(1)  # 1초마다 데이터를 보냄
            async with live_data_lock:
                await websocket.send_json(list(live_data.values()))  # JSON 형식으로 데이터 전송
            print("📤 [WebSocket 전송] 실시간 데이터 업데이트 완료")

    except WebSocketDisconnect:
        print("🔴 [WebSocket 연결 종료] 클라이언트가 연결을 끊었습니다.")
    except Exception as e:
        print(f"❌ [WebSocket 오류] {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
