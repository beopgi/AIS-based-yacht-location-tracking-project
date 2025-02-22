# app.py
# flake8: noqa
from dash import Dash, html, dcc, Input, Output, State
import dash_deck
import pydeck as pdk
import json
import websocket
import threading
import time

WEBSOCKET_SERVER = "ws://14.63.214.199:8080/ws"  # WebSocket 연결

# 화살표 아이콘 URL
ARROW_ICON_URL = "/assets/blue_arrow.png"

# Dash 앱 초기화
app = Dash(__name__)

# 지도 초기 좌표(부산)
initial_view = pdk.ViewState(
    latitude=35.112697,  
    longitude=129.124049,  
    zoom=11, 
    pitch=0, 
)

# 실시간 데이터 저장 변수
real_time_data = []

# WebSocket 연결 설정 및 자동 재연결 기능 추가
def websocket_listener():
    global real_time_data
    while True:
        try:
            ws = websocket.WebSocketApp(
                WEBSOCKET_SERVER,  # WebSocket 서버 주소
                on_message=lambda ws, msg: on_message(ws, msg),
                on_error=lambda ws, err: print(f"❌ [WebSocket 오류] {err}"),
                on_close=lambda ws, close_status, msg: print("🔴 [WebSocket 연결 종료], 재연결 시도 중..."),
            )
            print("🟢 [WebSocket 연결 시도] 서버에 연결 중...")
            ws.run_forever()
        except Exception as e:
            print(f"❌ [WebSocket 연결 실패] {e}, 5초 후 재연결 시도")
        time.sleep(5)  # 재연결을 위한 대기 시간

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
                html.Div(id="search-status", style={"marginLeft": "20px", "color": "white"}),
            ],
        ),
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
                    tooltip={"text": "{name}\nMMSI: {mmsi}\nSOG: {sog} knots\nCOG: {cog}\nStatus: {status}\nship_type: {ship_type}\ntime_utc: {time_utc}\nType_number: {Type_number}"},
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

def create_layers(ship_data, search_query=None):
    if search_query:
        search_query_lower = search_query.lower()
        filtered_data = [
            ship for ship in ship_data
            if str(ship.get("mmsi", "")) == search_query or search_query_lower == ship.get("name", "").lower()
        ]
    else:
        filtered_data = ship_data
        
    # 좌표가 없는 선박 필터링 (None, 0.0, "Unknown" 제거)
    filtered_data = [
        ship for ship in filtered_data 
        if ship.get("latitude") not in [None, "Unknown", 0.0] 
        and ship.get("longitude") not in [None, "Unknown", 0.0]
    ]

    icon_layer = pdk.Layer(
        "IconLayer",
        data=[
            {
                "coordinates": [ship["longitude"], ship["latitude"]],
                "name": ship.get("name", "Unknown"),
                "mmsi": ship.get("mmsi", "Unknown"),
                "sog": ship.get("sog", 0),
                "cog": ship.get("cog", 0),
                "ship_type": ship.get("ship_type", "Unknown"),
                "Type_number": ship.get("Type", 0),
                "true_heading": ship.get("true_heading", 0),
                "status": ship.get("navigational_status", "Unknown"),
                "time_utc": ship.get("time_utc", "Unknown"),
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
    return [icon_layer]

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

    layers = create_layers(real_time_data, search_query)
    deck = pdk.Deck(layers=layers, initial_view_state=initial_view)
    return deck.to_json(), "실시간 데이터 표시 중"

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
