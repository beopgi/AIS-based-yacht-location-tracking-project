# Server.py
# flake8: noqa
import asyncio
import json
from fastapi import FastAPI, WebSocket
import websockets

# FastAPI 앱 생성
app = FastAPI()

# 메모리 내 데이터 저장 (MMSI 기준 최신 데이터 유지)
live_data = {}

# 항해 상태 코드 변환 함수
def get_navigational_status_text(status_code):
    status_texts = {
        0: "항해중(엔진사용)",
        1: "정박 중",
        2: "조종 불능",
        3: "조종 제한",
        4: "흘수로인한 조종 제한",
        5: "계류 중",
        6: "좌초됨.",
        7: "조업중",
        8: "항해중(엔진사용X)",
        9: "유해물질 운반중 1",
        10: "유해물질 운반중 2",
        11: "뒤에서 견인",
        12: "앞에서 견인",
        13: "예약 상태",
        14: "구조 요청",
        15: "할당되지않음"
    }
    return status_texts.get(status_code, "Unknown")

# 실시간 데이터 수집
async def fetch_ship_data():
    """
    AIS 데이터를 지속적으로 수집하고 메모리에 저장.
    """
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "877c32d88cce08ea87119ba2736edcc0f6a6352d"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]  # 수집 범위

    async with websockets.connect(url) as websocket:
        subscribe_message = {
            "APIKey": api_key,
            "BoundingBoxes": bounding_boxes,
            "FiltersShipMMSI": [],
            "FilterMessageTypes": ["PositionReport"]
        }
        await websocket.send(json.dumps(subscribe_message))
        print("구독 메시지 전송 완료.")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if "MessageType" not in data or data["MessageType"] != "PositionReport":
                    continue

                ais_message = data["Message"]["PositionReport"]
                meta_data = data["MetaData"]

                # MMSI를 기준으로 메모리에 데이터 저장
                mmsi = meta_data.get("MMSI", "Unknown")
                live_data[mmsi] = {
                    "mmsi": mmsi,
                    "name": meta_data.get("ShipName", "Unknown").strip(),
                    "latitude": ais_message["Latitude"],
                    "longitude": ais_message["Longitude"],
                    "cog": ais_message.get("Cog", 0.0),
                    "sog": ais_message.get("Sog", 0.0),
                    "true_heading": ais_message.get("TrueHeading", 0.0),
                    "navigational_status": get_navigational_status_text(ais_message.get("NavigationalStatus", "Unknown")),
                    "time_utc": meta_data.get("time_utc", "Unknown")
                }

            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)

@app.on_event("startup")
async def start_data_collection():
    """
    서버가 시작될 때 데이터 수집 시작.
    """
    asyncio.create_task(fetch_ship_data())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    클라이언트 WebSocket 연결 관리.
    """
    await websocket.accept()

    # 클라이언트가 접속 시 현재 저장된 모든 데이터를 전송
    await websocket.send_json(list(live_data.values()))

    # 이후 실시간 데이터 스트리밍
    try:
        while True:
            await asyncio.sleep(1)  # 1초마다 갱신
            await websocket.send_json(list(live_data.values()))
    except Exception as e:
        print(f"WebSocket 연결 종료: {e}")

@app.get("/ships")
def get_all_ships():
    """
    메모리에 저장된 모든 데이터를 반환.
    """
    return list(live_data.values())
