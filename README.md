## 목표: 요트 실시간 추적 어플 만들기
설치해야하는것: streamlit, streamlit-folium, streamlit-autorefresh, pandas, requests
streamlit는 python으로 데이터 분석을 위한 웹앱을 쉽게 만들어주는 라이브러리이다.
streamlit 설치방법: vscode -> terminal -> cmd -> pip install streamlit -> streamlit hello -> 자신의 매일로 로그인인
대시보드 실행: streamlit run APP.py
지도: folium(추후 구글맵이나 카카오맵으로 변경)
데이터 수신: 해양수산부 선박위치정보(AIS) 통계정보 서비스

추후 해야하는것
streamlit sharing 에서 프로그램 배포해서 URL생성 -> 해양수산부에 오픈 API신청 -> API 받아서 지도에 출력
GPS로부터 API로 데이터를 직접 수신받는 경우 사용자가 직접 API를 입력 가능하게끔 제작
그외에 대시보드 디자인이라거나 편의성 증가같은 작업.



