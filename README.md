## 목표: 요트 실시간 추적 어플 만들기
streamlit는 python으로 데이터 분석을 위한 웹앱을 쉽게 만들어주는 라이브러리이다.
streamlit 설치방법: vscode -> terminal -> cmd -> pip install streamlit -> streamlit hello -> 자신의 매일로 로그인

대시보드 실행: streamlit run APP.py
지도: folium(추후 구글맵이나 카카오맵으로 변경할예정)
데이터 수신: 해양수산부 선박위치정보(AIS) 통계정보 서비스, GPS

향후 개발과정정
1. ~~대시보드 생성~~
2. ~~대시보드에 지도 추가~~
3. ~~모의데이터로 위치정보 표시~~
4. ~~streamlit sharing 에서 프로그램 배포해서 URL생성~~ 
5. ~~해양수산부에 오픈 API신청~~ 
6. 오픈 API를 통해 받은 해양수산부 AIS 데이터 편집
7. 대시보드 지도에 AIS 위치정보 실시간으로 표시
8. GPS로부터 API로 데이터를 직접 수신받는 경우 사용자가 직접 API를 입력 가능하게끔 제작
9. VHF주파수를 받아 표시할수있게끔 제작
10. 대시보드 디자인, 편의성 다듬기



