# app.py
# flake8: noqa
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from streamlit_autorefresh import st_autorefresh
import time

# FastAPI 서버 URL
API_URL = "http://localhost:8000/ships"


@st.cache_data(ttl=10)
def fetch_ship_data():
    """
    FastAPI 서버에서 선박 데이터를 가져오는 함수.
    데이터를 10초 동안 캐싱합니다.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"FastAPI 서버에서 데이터를 가져오지 못했습니다. 상태 코드: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류 발생: {e}")
        return []


def create_map(ship_data, center, zoom):
    """
    Folium 지도를 생성하고 선박 데이터를 지도에 표시합니다.
    """
    my_map = folium.Map(location=center, zoom_start=zoom)

    for ship in ship_data:
        latitude = ship.get("latitude", 0)
        longitude = ship.get("longitude", 0)
        sog = ship.get("sog", 0)
        true_heading = ship.get("true_heading", 0)
        cog = ship.get("cog", 0)
        direction_diff = abs(true_heading - cog)

        # 아이콘 각도 및 색상 설정
        if sog < 1:
            angle = true_heading
            icon_color = "gray"
        elif direction_diff > 10 and sog > 1:
            angle = cog
            icon_color = "red"
        else:
            angle = true_heading
            icon_color = "blue"

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(
                f"<b>Name:</b> {ship.get('name', 'Unknown')}<br>"
                f"<b>MMSI:</b> {ship.get('mmsi', 'Unknown')}<br>"
                f"<b>Latitude:</b> {latitude}<br>"
                f"<b>Longitude:</b> {longitude}<br>"
                f"<b>COG:</b> {cog}<br>"
                f"<b>SOG:</b> {sog}<br>"
                f"<b>True Heading:</b> {true_heading}<br>"
                f"<b>Status:</b> {ship.get('navigational_status', 'Unknown')}",
                max_width=250
            ),
            icon=folium.Icon(icon="arrow-up", angle=angle, color=icon_color, prefix="fa")
        ).add_to(my_map)

    return my_map


def main():
    st.title("AIS 기반 선박 위치 추적 대시보드")
    st.caption("실시간으로 AIS 데이터를 조회하고 선박의 상태를 확인하세요.")

    # 자동 새로고침: 10초마다 데이터 갱신
    st_autorefresh(interval=10000, key="data_refresh")

    # 검색어 상태 초기화
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    search_query = st.sidebar.text_input("선박 이름 또는 MMSI 검색", st.session_state.search_query)
    st.session_state.search_query = search_query

    # 지도 상태 초기화
    if "center" not in st.session_state:
        st.session_state.center = [37.5665, 126.9780]  # 서울 중심 좌표
    if "zoom" not in st.session_state:
        st.session_state.zoom = 6
    if "last_data" not in st.session_state:
        st.session_state.last_data = []  # 초기 데이터 저장
    if "last_update_time" not in st.session_state:
        st.session_state.last_update_time = time.time()  # 마지막 상태 업데이트 시간

    # 이전 지도 상태 가져오기
    center = st.session_state.center
    zoom = st.session_state.zoom

    # FastAPI 서버에서 데이터 가져오기
    ship_data = fetch_ship_data()

    # 검색어로 데이터 필터링
    if search_query:
        search_query_lower = search_query.lower()
        ship_data = [
            ship for ship in ship_data
            if search_query_lower in ship.get("name", "").lower() or search_query in ship.get("mmsi", "")
        ]

    # 데이터 변경 확인
    data_changed = ship_data != st.session_state.last_data
    if data_changed:
        st.session_state.last_data = ship_data  # 새로운 데이터로 업데이트

    # 지도 생성 및 표시
    current_data = st.session_state.last_data if st.session_state.last_data else []  # 기존 데이터를 사용
    my_map = create_map(current_data, center, zoom)
    map_data = st_folium(my_map, width=800, height=600, key="unique_map_key")

    # 지도 상태 업데이트: 1초 이상 가만히 있었을 경우
    if map_data and "center" in map_data and "lat" in map_data["center"] and "lng" in map_data["center"]:
        new_center = [map_data["center"]["lat"], map_data["center"]["lng"]]
        new_zoom = map_data["zoom"]

        current_time = time.time()
        time_since_last_update = current_time - st.session_state.last_update_time

        # 1초 이상 가만히 있었을 경우에만 상태 업데이트
        if time_since_last_update > 1 and (new_center != st.session_state.center or new_zoom != st.session_state.zoom):
            st.session_state.center = new_center
            st.session_state.zoom = new_zoom
            st.session_state.last_update_time = current_time

    # 상태 출력
    st.write(f"현재 지도 중심: {st.session_state.center}")
    st.write(f"현재 줌 레벨: {st.session_state.zoom}")


if __name__ == "__main__":
    main()