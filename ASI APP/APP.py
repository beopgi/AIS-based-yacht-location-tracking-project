# flake8: noqa
import streamlit as st
import pandas as pd
import numpy as np
import folium

# 데이터 삽입

# 지도 객체 생성 및 지도 초기 위치 설정(서울, 대한민국)
initial_location = [37.5665, 126.9780]
my_map = folium.Map(location=initial_location, zoom_start=6)
    
    
# 지도 커스텀
# 선박들 위치정보가 뿌려지면 그걸 삼각형 모양으로 지도에 찍어 준다.
# 그리고 지도는 데이터가 바뀔떄마다 새로고침을 한다. 


# 지도 제목과 캡션 추가
st.title('AIS기반 요트 위치추적적')
st.caption(
	"AIS를 이용하여 요트의 위치를 실시간으로 추적한다.")

# 지도 시각화
st.components.v1.html(my_map._repr_html_(), width=800, height=600)

# 버튼 삽입
st.button('버튼')