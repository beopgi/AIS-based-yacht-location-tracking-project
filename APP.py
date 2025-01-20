# app.py
# flake8: noqa
from dash import Dash, html, dcc, Input, Output, State
import dash_deck
import pydeck as pdk
import json
import websocket
import threading

# 화살표 아이콘 URL
ARROW_ICON_URL = "/assets/blue_arrow.png"

# Dash 앱 초기화
app = Dash(__name__)

# 초기 View 설정
initial_view = pdk.ViewState(
    latitude=37.5665,  # 서울 중심 좌표
    longitude=126.9780,
    zoom=6,
    pitch=0,
)

# 실시간 데이터 저장 변수
real_time_data = []

# WebSocket 연결 설정
def websocket_listener():
    global real_time_data
    ws = websocket.WebSocketApp(
        "ws://localhost:8000/ws",  # WebSocket 서버 주소
        on_message=lambda ws, msg: on_message(ws, msg),
        on_error=lambda ws, err: print(f"WebSocket 오류: {err}"),
        on_close=lambda ws, close_status, msg: print("WebSocket 연결 종료"),
    )
    ws.run_forever()

def on_message(ws, message):
    """
    WebSocket에서 메시지를 수신했을 때 호출.
    """
    global real_time_data
    try:
        real_time_data = json.loads(message)  # 실시간 데이터를 업데이트
    except Exception as e:
        print(f"데이터 처리 오류: {e}")

# WebSocket 스레드 시작
thread = threading.Thread(target=websocket_listener, daemon=True)
thread.start()

# 레이아웃 정의
app.layout = html.Div(
    style={"height": "100vh", "width": "100vw", "display": "flex", "flexDirection": "column"},
    children=[
        # 상단 검색 영역
        html.Div(
            style={
                "height": "60px",
                "backgroundColor": "#007bff",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "zIndex": "10",
            },
            children=[
                dcc.Input(
                    id="search-input",
                    type="text",
                    placeholder="MMSI 또는 선박 이름으로 검색",
                    debounce=True,
                    style={"width": "300px", "padding": "10px", "borderRadius": "5px", "zIndex": "10"},
                ),
                html.Button(
                    "검색", id="search-button", n_clicks=0, style={"marginLeft": "10px", "padding": "10px"}
                ),
                html.Div(id="search-status", style={"marginLeft": "20px", "color": "white"}),  # 검색 상태 표시
            ],
        ),
        # 지도 영역
        html.Div(
            id="map-container",
            style={
                "flex": "1",
                "position": "relative",
                "zIndex": "1",
            },
            children=[
                dash_deck.DeckGL(
                    id="deck-gl",
                    mapboxKey="",
                    style={
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "zIndex": "1",
                    },
                    data={},
                    tooltip={"text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}"},
                ),
                dcc.Interval(
                    id="interval-component",
                    interval=5000,  # 5초마다 콜백 호출
                    n_intervals=0,
                ),
            ],
        ),
    ],
)

# Pydeck Layer 생성
def create_layers(ship_data, search_query=None):
    """
    ship_data: 실시간으로 수신된 선박 데이터 (리스트 형식)
    search_query: 검색어 (MMSI 또는 선박 이름)
    """
    # 검색 결과 필터링
    if search_query:
        search_query_lower = search_query.lower()
        filtered_data = [
            ship for ship in ship_data
            if str(ship.get("mmsi", "")) == search_query or search_query_lower == ship.get("name", "").lower()
        ]
    else:
        filtered_data = ship_data

    icon_layer = pdk.Layer(
        "IconLayer",
        data=[
            {
                "coordinates": [ship["longitude"], ship["latitude"]],
                "name": ship.get("name", "Unknown"),
                "mmsi": ship.get("mmsi", "Unknown"),
                "sog": ship.get("sog", 0),
                "cog": ship.get("cog", 0),
                "status": ship.get("navigational_status", "Unknown"),
                "icon": {
                    "url": ARROW_ICON_URL,
                    "width": 128,
                    "height": 128,
                    "anchorY": 128,
                },
            }
            for ship in filtered_data
        ],
        get_position="coordinates",
        get_icon="icon",
        get_angle="true_heading",
        size_scale=15,
        pickable=True,
    )

    tile_layer = pdk.Layer(
        "TileLayer",
        data="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        get_tile_url_params={"s": "a"},
    )

    return [tile_layer, icon_layer], len(filtered_data)

# Dash 콜백: 지도 데이터 업데이트
@app.callback(
    Output("deck-gl", "data"),
    Output("search-status", "children"),
    Input("interval-component", "n_intervals"),
    Input("search-button", "n_clicks"),
    State("search-input", "value"),
)
def update_map(n_intervals, n_clicks, search_query):
    global real_time_data

    if not real_time_data:
        deck = pdk.Deck(initial_view_state=initial_view)
        return deck.to_json(), "실시간 데이터 없음"

    # 검색 조건 확인
    if n_clicks and search_query:
        search_query_lower = search_query.lower()
        filtered_data = [
            ship for ship in real_time_data
            if str(ship.get("mmsi", "")) == search_query or search_query_lower == ship.get("name", "").lower()
        ]
        if not filtered_data:
            return pdk.Deck(initial_view_state=initial_view).to_json(), "검색 결과 없음"

        layers, result_count = create_layers(filtered_data)
        deck = pdk.Deck(
            layers=layers,
            initial_view_state=initial_view,
            tooltip={"text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}"},
        )
        return deck.to_json(), f"검색 결과: {result_count}개"

    # 검색 조건이 없을 경우 전체 데이터를 표시
    layers, _ = create_layers(real_time_data)
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view,
        tooltip={"text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}"},
    )
    return deck.to_json(), "실시간 데이터 표시 중"

if __name__ == "__main__":
    app.run_server(debug=True)
