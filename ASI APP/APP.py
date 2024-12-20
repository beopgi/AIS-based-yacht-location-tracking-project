# flake8: noqa
# APP.py
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# API 호출을 위한 함수
def fetch_ship_data():
    # API URL 및 인증 키 설정
    url = "http://www.gicoms.go.kr/kodispub/openApi/wms.do?"
    api_key = st.secrets["api"]["serviceKey"]

    # API 요청에 필요한 파라미터 설정
    params = {
        'serviceKey': api_key,
        'type': 'json',
        'numOfRows': 10,
        'pageNo': 1
    }
    try:
        # API 호출 및 응답 처리
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        data = response.json()  # JSON 데이터로 변환
        return data.get('items', [])  # 'items' 키가 없을 경우 빈 리스트 반환
    except requests.RequestException as e:
        # 요청 예외 발생 시 에러 메시지 출력 및 모의 데이터 반환
        st.error(f"API 데이터를 가져오는 데 실패했습니다. 모의 데이터를 표시합니다: {e}")
        return fetch_mock_data()

# 모의 데이터 함수
def fetch_mock_data():
    return [
        {"name": "Yacht A", "latitude": 37.4500, "longitude": 132.0000},
        {"name": "Yacht B", "latitude": 34.0000, "longitude": 127.0000},
        {"name": "Yacht C", "latitude": 37.5000, "longitude": 124.5000}
    ]

# 데이터 처리 함수
def process_data(data):
    # 데이터가 없을 경우 빈 데이터프레임 반환
    if not data:
        return pd.DataFrame()
    try:
        # 데이터프레임으로 변환 및 위도, 경도 데이터 형 변환
        ship_data = pd.DataFrame(data)
        ship_data['lat'] = ship_data['latitude'].astype(float)  # 위도 입력
        ship_data['lon'] = ship_data['longitude'].astype(float)  # 경도 입력
        return ship_data
    except KeyError as e:
        # 필수 데이터 키가 누락된 경우 에러 메시지 출력
        st.error(f"필수 데이터 키가 누락되었습니다: {e}")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    except ValueError as e:
        # 데이터 형 변환 오류 발생 시 에러 메시지 출력
        st.error(f"데이터 형식 변환 오류: {e}")
        return pd.DataFrame()  # 빈 데이터프레임 반환

# 지도 생성 함수
def create_map(ship_data, current_location):
    # 데이터프레임이 비어 있을 경우 경고 메시지 출력
    if ship_data.empty:
        st.warning("지도 생성에 필요한 데이터가 없습니다.")
        return None

    # 지도 초기 설정 (기본값: 서울, 대한민국 좌표)
    my_map = folium.Map(location=current_location, zoom_start=6)

    # 데이터프레임의 각 행에 대해 마커 추가
    for index, row in ship_data.iterrows():
        folium.RegularPolygonMarker(
            location=[row['lat'], row['lon']],  # 위도와 경도 설정
            fill=True,
            fill_color='blue',
            number_of_sides=3,  # 삼각형 모양 마커
            radius=10,  # 마커 크기
            popup=f"Ship: {row.get('name', 'Unknown')}\nLat: {row['lat']}\nLon: {row['lon']}"  # 팝업 정보
        ).add_to(my_map)

    return my_map

# 메인 함수
def main():
    # 제목과 설명 표시
    st.title('AIS기반 요트 위치추적')
    st.caption("AIS를 이용하여 요트의 위치를 실시간으로 추적한다.")

    # 초기 지도 중심 위치 설정
    if 'center' not in st.session_state:
        st.session_state.center = [37.5665, 126.9780]

    # 자동 새로고침 설정 (3000ms = 3초)
    st_autorefresh(interval=3000, key="data_refresh")

    # 데이터 가져오기 및 처리
    data = fetch_ship_data()  # API 데이터 호출
    ship_data = process_data(data)  # 데이터 처리

    # 지도 생성 및 시각화
    if not ship_data.empty:
        my_map = create_map(ship_data, st.session_state.center)  # 지도 생성
        if my_map:
            # Folium 지도를 Streamlit 앱에 표시
            map_state = st_folium(my_map, width=800, height=600)

            # 현재 지도 중심 위치 업데이트
            if map_state["last_active_drawing"]:
                st.session_state.center = map_state["last_active_drawing"]["geometry"]["coordinates"][::-1]
    else:
        # 데이터가 없을 경우 경고 메시지 표시
        st.warning("표시할 데이터가 없습니다. API 응답을 확인하세요.")

# 프로그램 시작
if __name__ == '__main__':
    main()
