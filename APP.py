# APP.py
# flake8: noqa
import asyncio
import websockets
import json
import requests
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import nest_asyncio

# nest_asyncio 활성화
nest_asyncio.apply()

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

# 웹소켓을 통해 실시간 데이터 가져오는 함수
async def fetch_ship_data(stop_event):
    url = "wss://stream.aisstream.io/v0/stream"
    api_key = "877c32d88cce08ea87119ba2736edcc0f6a6352d"
    bounding_boxes = [[[33.0, 124.0], [38.0, 130.0]]]

    try:
        async with websockets.connect(url, open_timeout=10, ping_timeout=10) as websocket:
            subscribe_message = {
                "APIKey": api_key,
                "BoundingBoxes": bounding_boxes,
                "FiltersShipMMSI": [],
                "FilterMessageTypes": ["PositionReport"]
            }
            await websocket.send(json.dumps(subscribe_message))

            while not stop_event.is_set():
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # 터미널 출력 추가
                    print(json.dumps(data, indent=4))

                    if "MessageType" not in data:
                        continue

                    if data["MessageType"] == "PositionReport":
                        ais_message = data["Message"]["PositionReport"]
                        meta_data = data["MetaData"]
                        navigational_status = get_navigational_status_text(ais_message.get("NavigationalStatus", "Unknown"))

                        yield {
                            "name": meta_data.get("ShipName", "Unknown").strip(),
                            "latitude": ais_message["Latitude"],
                            "longitude": ais_message["Longitude"],
                            "mmsi": meta_data.get("MMSI", "Unknown"),
                            "time_utc": meta_data.get("time_utc", "Unknown"),
                            "cog": ais_message.get("Cog", "Unknown"),
                            "true_heading": ais_message.get("TrueHeading", "Unknown"),
                            "navigational_status": navigational_status,
                            "sog": ais_message.get("Sog", "Unknown")
                        }

                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Connection closed: {e}. Reconnecting...")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break
    except Exception as e:
        print(f"WebSocket connection failed: {e}")

# 지도 생성 함수
def create_map(ship_data, current_location, search_query=None):
    my_map = folium.Map(location=current_location, zoom_start=6)  # 기본 위치와 확대 수준 사용

    if not ship_data.empty:
        for _, row in ship_data.iterrows():
            if row['latitude'] == 'Unknown' or row['longitude'] == 'Unknown':
                continue

            sog = row.get('sog', 0)
            true_heading = row.get('true_heading', 0)
            cog = row.get('cog', 0)

            angle = 0
            direction_diff = abs(true_heading - cog)
            if sog < 1:
                angle = true_heading
                icon_color = 'gray'
            elif direction_diff > 10 and sog > 1:
                angle = cog
                icon_color = 'red'
            else:
                angle = true_heading
                icon_color = 'blue'

            # 검색된 선박의 마커 색상을 빨간색으로 변경
            if search_query and (search_query in str(row['mmsi']) or search_query in row['name']):
                icon_color = 'green'
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(f"ShipName: {row.get('name', 'Unknown')}<br>"
                                       f"MMSI: {row.get('mmsi', 'Unknown')}<br>"
                                       f"Latitude: {row['latitude']}<br>"
                                       f"Longitude: {row['longitude']}<br>"
                                       f"COG: {cog}<br>"
                                       f"SOG: {sog}<br>"
                                       f"True Heading: {true_heading}<br>"
                                       f"Navigational Status: {row.get('navigational_status', 'Unknown')}<br>"
                                       f"Last Update: {row.get('time_utc', 'Unknown')}", max_width=200),
                    icon=folium.Icon(icon='arrow-up', angle=angle, color=icon_color, prefix='fa')
                ).add_to(my_map)
            else:
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(f"ShipName: {row.get('name', 'Unknown')}<br>"
                                       f"MMSI: {row.get('mmsi', 'Unknown')}<br>"
                                       f"Latitude: {row['latitude']}<br>"
                                       f"Longitude: {row['longitude']}<br>"
                                       f"COG: {cog}<br>"
                                       f"SOG: {sog}<br>"
                                       f"True Heading: {true_heading}<br>"
                                       f"Navigational Status: {row.get('navigational_status', 'Unknown')}<br>"
                                       f"Last Update: {row.get('time_utc', 'Unknown')}", max_width=200),
                    icon=folium.Icon(icon='arrow-up', angle=angle, color=icon_color, prefix='fa')
                ).add_to(my_map)

    return my_map

async def main_task(stop_event):
    try:
        async for data_chunk in fetch_ship_data(stop_event):
            if data_chunk:
                new_data = pd.DataFrame([data_chunk])
                existing_data = pd.DataFrame(st.session_state.ship_data)
                combined_data = pd.concat([existing_data, new_data])
                combined_data.drop_duplicates(subset=['mmsi'], keep='last', inplace=True)
                st.session_state.ship_data = combined_data.to_dict('records')
                if not st.session_state.search_query:
                    st.session_state.center = [combined_data.iloc[0]['latitude'], combined_data.iloc[0]['longitude']]
    except Exception as e:
        st.error(f"데이터 수집 중 오류 발생: {e}")

async def main():
    st.title('AIS 기반 선박 위치 추적')
    st.caption("AIS 실시간 선박 위치 추적 시스템")
    st.caption("스피드가 1이하인 배는 회색으로 표시")
    

    with st.sidebar:
        search_query = st.text_input("MMSI 또는 배 이름 검색", "")
        if st.button('검색'):
            st.session_state.search_query = search_query

    if 'center' not in st.session_state:
        st.session_state.center = [37.5665, 126.9780]
    if 'ship_data' not in st.session_state:
        st.session_state.ship_data = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'stop_event' not in st.session_state:
        st.session_state.stop_event = asyncio.Event()
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    if st.button('실시간 데이터 수집 시작'):
        st.session_state.running = True
        st.session_state.stop_event.clear()
        st.session_state.center = [37.5665, 126.9780]  # Reset to initial coordinates

    if st.button('실시간 데이터 수집 중지'):
        st.session_state.running = False
        st.session_state.stop_event.set()

    if st.session_state.running:
        await main_task(st.session_state.stop_event)
    else:
        if st.session_state.ship_data:
            ship_data = pd.DataFrame(st.session_state.ship_data)
            my_map = create_map(ship_data, st.session_state.center, st.session_state.search_query)
            st_folium(my_map, width=800, height=600)
            #st.session_state.search_query = ""  # Reset search query

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
