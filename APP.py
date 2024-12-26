# APP.py
# flake8: noqa
import asyncio
import websockets
import json
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import nest_asyncio

# nest_asyncio 활성화
nest_asyncio.apply()

# 웹소켓을 통해 실시간 데이터 가져오는 함수
async def fetch_ship_data(stop_event):
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "877c32d88cce08ea87119ba2736edcc0f6a6352d"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]  # 대한민국 주변 좌표

    try:
        # 웹소켓 연결 설정 및 연결
        async with websockets.connect(url, open_timeout=10, ping_timeout=10) as websocket:
            # 구독 메시지 전송
            subscribe_message = {
                "APIKey": api_key,
                "BoundingBoxes": bounding_boxes,
                "FiltersShipMMSI": [],
                "FilterMessageTypes": ["PositionReport"]
            }
            await websocket.send(json.dumps(subscribe_message))

            # 데이터 수집
            while not stop_event.is_set():
                try:
                    # 메시지 수신
                    message = await websocket.recv()
                    data = json.loads(message)

                    # 메시지 유형 확인
                    if "MessageType" not in data:
                        continue

                    # PositionReport 처리
                    if data["MessageType"] == "PositionReport":
                        ais_message = data["Message"]["PositionReport"]
                        meta_data = data["MetaData"]

                        yield {
                            "name": meta_data.get("ShipName", "Unknown").strip(),
                            "latitude": ais_message["Latitude"],
                            "longitude": ais_message["Longitude"],
                            "mmsi": meta_data.get("MMSI", "Unknown"),
                            "time_utc": meta_data.get("time_utc", "Unknown")
                        }
                except websockets.exceptions.ConnectionClosedError as e:
                    # 연결이 닫힌 경우 재연결 시도
                    print(f"Connection closed: {e}. Reconnecting...")
                    await asyncio.sleep(1)
                except Exception as e:
                    # 기타 예외 처리
                    print(f"Unexpected error: {e}")
                    break
    except Exception as e:
        # 웹소켓 연결 실패 처리
        print(f"WebSocket connection failed: {e}")

# 지도 생성 함수
def create_map(ship_data, current_location):
    # 초기 지도 설정
    my_map = folium.Map(location=current_location, zoom_start=6)

    if not ship_data.empty:
        # 각 선박의 위치에 마커 추가
        for _, row in ship_data.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=(
                    f"ShipName: {row.get('name', 'Unknown')}\n"
                    f"MMSI: {row.get('mmsi', 'Unknown')}\n"
                    f"Latitude: {row['latitude']}\n"
                    f"Longitude: {row['longitude']}\n"
                    f"Last Update: {row.get('time_utc', 'Unknown')}"
                ),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(my_map)

    return my_map

# 비동기 데이터 수집 및 처리 함수
async def main_task(stop_event):
    try:
        # 실시간 데이터 수집
        async for data_chunk in fetch_ship_data(stop_event):
            if data_chunk:
                # 수신된 데이터 출력
                print(f"Received data: {data_chunk}")
                
                # 데이터프레임으로 변환 후 기존 데이터와 결합
                new_data = pd.DataFrame([data_chunk])
                existing_data = pd.DataFrame(st.session_state.ship_data)
                combined_data = pd.concat([existing_data, new_data])
                
                # MMSI와 이름을 기준으로 중복 항목 제거
                combined_data.drop_duplicates(subset=['mmsi', 'name'], keep='last', inplace=True)
                st.session_state.ship_data = combined_data.to_dict('records')
                
                # 지도 업데이트
                ship_data = combined_data
                st.session_state.center = [ship_data.iloc[0]['latitude'], ship_data.iloc[0]['longitude']]
    except StopAsyncIteration:
        pass
    except Exception as e:
        # 데이터 수집 중 오류 발생 처리
        st.error(f"데이터 수집 중 오류 발생: {e}")

# 메인 함수
async def main():
    st.title('AIS 기반 요트 위치 추적')
    st.caption("AIS를 이용한 실시간 요트 위치 추적 시스템")

    # 세션 상태 초기화
    if 'center' not in st.session_state:
        st.session_state.center = [37.5665, 126.9780]
    if 'ship_data' not in st.session_state:
        st.session_state.ship_data = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'stop_event' not in st.session_state:
        st.session_state.stop_event = asyncio.Event()

    # 버튼 UI
    col1, col2 = st.columns(2)
    with col1:
        if st.button('실시간 데이터 수집 시작'):
            st.session_state.running = True
            st.session_state.stop_event.clear()
    with col2:
        if st.button('실시간 데이터 수집 중지'):
            st.session_state.running = False
            st.session_state.stop_event.set()

    # 데이터 스트림 처리
    if st.session_state.running:
        await main_task(st.session_state.stop_event)
    else:
        # 실시간 데이터 수집이 중단되었을 때 마지막 위치의 지도를 그립니다.
        if st.session_state.ship_data:
            ship_data = pd.DataFrame(st.session_state.ship_data)
            my_map = create_map(ship_data, st.session_state.center)
            st_folium(my_map, width=800, height=600)

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
