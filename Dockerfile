# 1. Python 3.9 기반 이미지 사용
FROM python:3.9

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 현재 폴더 내 모든 파일을 컨테이너에 복사
COPY . .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 두 개의 Python 프로세스를 동시에 실행
CMD ["sh", "-c", "python Server.py & python APP.py"]

# 포트 개방 추가
EXPOSE 8000 8050
