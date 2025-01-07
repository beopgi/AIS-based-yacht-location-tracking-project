## 목표: 요트 실시간 추적 어플 만들기
streamlit는 python으로 데이터 분석을 위한 웹앱을 쉽게 만들어주는 라이브러리이다.
streamlit 설치방법: vscode -> terminal -> cmd -> pip install streamlit -> streamlit hello -> 자신의 매일로 로그인

대시보드 실행: streamlit run APP.py
서버 실행: uvicorn Server:app --reload
대시보드 밑 서버 종료: ctrl + c
지도: folium(추후 구글맵이나 카카오맵으로 변경할예정)
데이터 수신: aisstream.io(AIS), GPS

웹소켓이 뭔지 설명 추가가
양방향 통신: 클라이언트(예: 웹 브라우저)와 서버가 서로 데이터를 주고받을 수 있습니다. 한쪽에서 데이터를 보내면 실시간으로 다른 쪽에서 바로 받을 수 있습니다.

지속적인 연결: 일반적인 HTTP 요청과 달리, 웹소켓 연결은 한번 열리면 클라이언트와 서버 간의 지속적인 연결이 유지됩니다. 이로 인해 실시간 데이터 업데이트가 가능합니다.

낮은 오버헤드: 기존의 HTTP 요청에 비해 데이터 전송 시 헤더가 적어 오버헤드가 낮습니다. 따라서 실시간 데이터를 더 효율적으로 주고받을 수 있습니다.

MMSI를 입력해서 해당 선박의 위치 데이터만 따로 표시가능

[대시보드 링크](https://ais-based-yacht-location-tracking-project-9yjkzxsj8ymkkbzljzbb.streamlit.app/)

개발과정
1. ~~대시보드 생성~~
2. ~~대시보드에 지도 추가~~
3. ~~모의데이터로 위치정보 표시~~
4. ~~streamlit sharing 에서 프로그램 배포해서 URL생성~~ 
5. ~~aisstream.io에 오픈 API신청~~
6. ~~오픈 API를 통해 받은 aisstream.io AIS 데이터 편집~~
7. ~~대시보드 지도에 AIS 위치정보 실시간으로 표시~~
8. ~~fastapi로 서버 제작~~
9. 대시보드 디자인, 편의성 다듬기

국제 해양법: 선박의 길이와 폭에 따라 분류함.
소형 선박: 길이가 20미터 이하, 폭 6미터 이하
중형 선박: 길이가 20미터 ~ 50미터,폭이 6미터 ~ 15미터
대형 선박: 50미터 이상, 폭 15미터 이상