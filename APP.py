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

    style={
        "height": "100vh",
        "width": "100vw",
        "display": "flex",
        "flex-direction": "column",
    },
    children=[
        # 상단 네비게이션 바
        html.Div(
            style={
                "height": "50px",
                "width": "100%",
                "background-color": "#007bff",
                "display": "flex",
                "align-items": "center",
                "justify-content": "space-between",
                "padding": "0 20px",
                "color": "white",
                "font-size": "20px",
            },
            children=[
                html.Div("", style={"font-weight": "bold"}),
                html.Div(
                    dcc.Input(
                        id="nav-search",
                        type="text",
                        placeholder="mmsi 또는 ship_name으로 검색",
                        style={"padding": "5px", "width": "200px"},
                    ),
                    style={"display": "flex", "align-items": "center"},
                ),
            ],
        ),
        # 메인 콘텐츠 영역
        html.Div(
            style={
                "flex": "1",
                "display": "flex",
                "position": "relative",
            },
            children=[
                # 슬라이드 패널
                html.Div(
                    id="sidebar",
                    style={
                        "width": "300px",
                        "height": "100%",
                        "position": "absolute",
                        "top": "0",
                        "left": "-300px",  # 숨겨진 상태에서 시작
                        "background-color": "#f9f9f9",
                        "box-shadow": "2px 0px 5px rgba(0,0,0,0.1)",
                        "padding": "20px",
                        "transition": "left 0.3s ease-in-out",  # 애니메이션 효과
                    },
                    children=[
                        html.H3("검색 결과", style={"text-align": "center"}),
                        dcc.Input(
                            id="search-input",
                            type="text",
                            placeholder="선박 이름 또는 MMSI 검색",
                            debounce=True,
                            style={
                                "width": "90%",
                                "padding": "10px",
                                "margin": "10px auto",
                                "display": "block",
                            },
                        ),
                        html.Div(id="search-status"),
                        dcc.Interval(id="interval-component", interval=10000, n_intervals=0),  # 10초마다 지도 갱신
                    ],
                ),
                # 지도 영역
                html.Div(
                    id="map-container",
                    style={
                        "flex": "1",
                        "position": "absolute",
                        "top": "0",
                        "left": "0",
                        "right": "0",
                        "bottom": "0",
                        "z-index": "1",
                    },
                    children=[
                        dash_deck.DeckGL(
                            id="deck-gl",
                            mapboxKey="",  # Mapbox API 키 필요 없음
                            style={"width": "100%", "height": "100%"},
                            data={},  # 초기 데이터
                            tooltip={
                                "text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}"
                            },
                        )
                    ],
                ),
                # 슬라이드 버튼
                html.Button(
                    "☰",
                    id="sidebar-toggle",
                    n_clicks=0,
                    style={
                        "position": "absolute",
                        "top": "10px",
                        "left": "10px",
                        "z-index": "1000",
                        "background-color": "#007bff",
                        "color": "#fff",
                        "border": "none",
                        "padding": "10px",
                        "border-radius": "5px",
                        "cursor": "pointer",
                    },
                ),
            ],
        ),
    ],
)

# 슬라이드 버튼 콜백
@app.callback(
    Output("sidebar", "style"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar", "style"),
)
def toggle_sidebar(n_clicks, sidebar_style):
    if n_clicks % 2 == 1:  # 홀수 클릭: 열기
        sidebar_style["left"] = "0px"
    else:  # 짝수 클릭: 닫기
        sidebar_style["left"] = "-300px"
    return sidebar_style

# Pydeck Layer 생성
def create_layers(ship_data, search_query):
    """
    ship_data: 실시간으로 수신된 선박 데이터 (리스트 형식)
    search_query: 검색어 (선박 이름 또는 MMSI)
    """
    # 검색 결과 필터링
    if search_query:
        search_query_lower = search_query.lower()
        filtered_data = [
            ship for ship in ship_data
            if search_query_lower in ship.get("name", "").lower() or search_query in ship.get("mmsi", "")
        ]
    else:
        filtered_data = ship_data

    # Pydeck 레이어 생성
    icon_layer = pdk.Layer(
        "IconLayer",
        data=[
            {
                "coordinates": [ship["longitude"], ship["latitude"]],
                "name": ship.get("name", "Unknown"),
                "mmsi": ship.get("mmsi", "Unknown"),
                "sog": ship.get("sog", 0),
                "cog": ship.get("cog", 0),
                "true_heading": ship.get("true_heading", 0),
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

    # OpenStreetMap TileLayer 추가
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
    Input("search-input", "value"),
)
def update_map(n_intervals, search_query):
    global real_time_data

    # 레이어 생성 및 검색 결과 개수 반환
    layers, result_count = create_layers(real_time_data, search_query)

    # Pydeck 객체 생성
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view,
        tooltip={
            "text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}"
        },
    )

    # 상태 메시지 업데이트
    status_message = f"검색어: {search_query or '없음'}, 검색 결과: {result_count}개"

    return deck.to_json(), status_message

if __name__ == "__main__":
    app.run_server(debug=True)
