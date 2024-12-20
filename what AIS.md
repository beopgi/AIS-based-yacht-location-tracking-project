# AIS(Automatic Identification System) 개요

AIS는 해양 교통 안전과 효율적인 관리에 중요한 역할을 하는 자동 식별 시스템입니다. 선박의 위치, 속도, 항로 등의 정보를 실시간으로 전송하여 선박 간의 충돌을 방지하고, 해양 교통을 효과적으로 관리합니다.

---

## 1. AIS란 무엇인가?
AIS는 선박에 탑재된 장치와 해양 기지국 간 데이터를 송수신하는 시스템으로, 다음과 같은 정보를 제공합니다:

- **정적 정보**: 선박 이름, IMO 번호, MMSI 번호, 선박 유형, 크기 등과 같이 고정된 데이터.
- **동적 정보**: GPS를 기반으로 실시간으로 업데이트되는 위치, 속도, 항로, 항해 상태 등.

---

## 2. AIS의 주요 구성 요소
AIS 시스템을 구성하는 핵심 장비는 다음과 같습니다:

### 2.1 GPS 수신기
- 위성 신호를 통해 선박의 정확한 위치를 계산.
- AIS 데이터의 기본이 되는 실시간 위치 정보 제공.

### 2.2 AIS 트랜스폰더
- GPS에서 수집된 데이터와 정적 정보를 디지털 변조하여 VHF 주파수로 전송.

### 2.3 VHF 라디오 및 안테나
- AIS 통신을 위해 161.975 MHz(AIS 1)와 162.025 MHz(AIS 2) 주파수를 사용.
- 직선 전파 특성으로 먼 거리까지 신호를 안정적으로 전달하며, 짧은 안테나로도 효율적인 통신 가능.

### 2.4 NMEA 0183 프로토콜
- GPS 데이터와 기타 항해 정보를 표준 포맷으로 변환해 통신 장비 간 연동.

### 2.5 해양 기지국
- 선박으로부터 AIS 데이터를 수신하여 해양 교통 관리 센터에 전달.

### 2.6 소프트웨어 애플리케이션
- AIS 데이터를 시각화하고 분석하여, 해양 교통 모니터링 및 사고 방지 지원.

---

## 3. AIS의 작동 원리

### 3.1 데이터 수집 및 전송
1. **GPS 데이터 수집**: 선박의 위치, 속도, 방향 등의 정보를 GPS를 통해 수집.
2. **NMEA 0183 포맷 변환**: 수집된 데이터를 표준 포맷으로 변환.
3. **VHF 송신**: 변환된 데이터를 AIS 트랜스폰더가 디지털 변조 후 VHF 주파수로 전송.

### 3.2 데이터 송수신 방식
- **TDMA(Time Division Multiple Access)**: 선박 간 충돌 없는 데이터 전송을 위해 시간 슬롯 기반 전송 방식 사용.
  - 각 선박은 고유 시간 슬롯을 할당받아 데이터를 송신.

#### TDMA 예시:
전체 1초를 10개의 시간 슬롯으로 나눕니다. 
- **슬롯 1**: 선박 A가 데이터 전송.
- **슬롯 2**: 선박 B가 데이터 전송.
- 이 과정을 반복하여 신호 충돌 없이 정보를 효율적으로 전달합니다.

### 3.3 선박간의 데이터 수신 및 복호화
1. 주변의 다른 선박들은 VHF 수신기를 통해 송신된 신호를 수신하고, 디지털 신호로 복호화하여 원래의 데이터로 복원합니다. 이렇게 하면 선박 간에 실시간으로 위치 정보를 공유할 수 있습니다.(API를 사용하는건 순전히 소프트웨어 애프리케이션에서 쉽게 접근하고 활용하기 위해서 입니다. VHF로 수신된 데이터는 복호화를 통해 확인 가능합니다. VHF로 수신된 데이터를 실시간으로 확인할 수 있지만, API를 사용하면 이 데이터를 효과적으로 관리하고 활용할 수 있습니다.)

---

## 4. AIS의 두 가지 유형

### 4.1 Class A
- 대형 상업용 선박과 여객선에서 사용.
- 출력: 12.5W
- 특징: 더 긴 거리와 빈번한 데이터 전송 간격.

### 4.2 Class B
- 소형 선박이나 개인용 보트에서 사용.
- 출력: 2W
- 특징: 간헐적 데이터 전송.

---

## 5. AIS 데이터 처리와 API 활용

### 5.1 데이터 처리 과정
1. **데이터 수집**: GPS를 통해 선박의 위치, 속도, 방향 등의 데이터를 수집하고, AIS 시스템에서 이를 통합하여 처리합니다.
2. **VHF 송신 및 수신**: 데이터를 VHF를 통해 송수신.
3. **복호화**: 수신된 신호를 디지털 데이터로 변환.
4. **API를 통한 활용**: 데이터를 외부 소프트웨어로 제공하여 실시간 분석 및 모니터링.

### 5.2 API란 무엇인가?
API(Application Programming Interface)는 소프트웨어와 시스템 간의 데이터 교환을 가능하게 하는 인터페이스입니다. 이를 통해 다른 애플리케이션이나 서비스와 쉽게 통신하고 데이터를 주고받을 수 있습니다. 

AIS 시스템에서는 API가 다음과 같은 역할을 수행합니다:
- 외부 소프트웨어가 AIS 데이터를 실시간으로 가져올 수 있도록 지원.
- 데이터를 표준화된 형식으로 제공하여 다양한 응용 프로그램에서 일관되게 활용 가능.
- 항로 계획, 해상 사고 관리, 물류 최적화 등 여러 시스템 간의 연동을 간소화. 이를 통해 다음과 같은 다양한 응용이 가능합니다:

- **항로 계획 소프트웨어**: 실시간 위치 데이터를 기반으로 안전한 항로를 설계.
- **해상 재난 관리 시스템**: 긴급 상황 시 선박 위치를 파악하고 대응.
- **실시간 물류 관리**: 화물선의 경로 및 도착 시간을 추적하여 물류 최적화.
- **해양 환경 모니터링 시스템**: 특정 해역에서의 선박 활동 데이터를 수집하여 환경 영향을 분석.
- **선박 자동화 시스템**: 자율 운항 선박에서 경로 및 주변 선박 데이터를 실시간으로 처리.
- 해상 재난 관리 시스템.
- 실시간 물류 관리.
- 해양 환경 모니터링 시스템.


---

## 6. AIS와 최신 기술의 융합
- **AI 기술**: 자율 선박 운영과 해양 사고 예측에 활용.
- **IoT 기술**: 실시간 데이터 연결을 통한 스마트 해양 교통 관리.

---

## 7. 결론
AIS는 선박 간 충돌 방지와 해양 교통 관리에 핵심적인 역할을 합니다. VHF 통신, GPS 데이터, API 등을 통해 실시간 데이터를 처리하며, 해양 안전과 효율성을 높이고 있습니다. 향후 AI 및 IoT와의 융합으로 더욱 발전된 해양 관리 시스템으로 진화할 것입니다.


AIS API: 해양 교통 관리 시스템, 항로 계획 소프트웨어 등에서 실시간 선박 위치 데이터를 수집하고 분석하는 데 사용됩니다. AIS API를 통해 소프트웨어 애플리케이션은 AIS 데이터를 실시간으로 가져와서, 해양 교통 상황을 모니터링하고, 선박의 안전한 운항을 지원할 수 있습니다.

---

# AIS 등록 없이 선박의 위치를 실시간으로 추적 방법

## 1. GPS 설치
선박에 GPS 수신기를 설치하여 위치 정보를 수집합니다. GPS는 위성 신호를 통해 선박의 정확한 위치를 제공합니다.

## 2. 데이터 전송 네트워크 설정
GPS에서 수집한 데이터를 전송하기 위해 LTE, 위성통신, Wi-Fi 등의 데이터 전송 네트워크를 설정합니다.

### 2.1 서버 및 데이터 처리(데이터를 지속적으로 저장할 필요가 있는경우)
- **데이터 수신 서버**: GPS 장치에서 전송된 데이터를 수신할 수 있는 서버를 구축합니다.
- **데이터베이스 설정**: 수신된 위치 데이터를 저장하기 위해 데이터베이스를 설정합니다.

## 3. 데이터 수신
GPS 장치는 각각 고유의 API와 key가 할당 되있습니다. 이를 통해 GPS에서 API를 통해 데이터를 실시간으로 수신합니다.

## 결론
AIS 시스템은 VHF 주파수를 통해 데이터를 전송하고 API를 통해 처리하여 해양 선박들을 효율적으로 관리하는 시스템입니다. 하지만, AIS에 등록되지 않은 선박의 경우에도 GPS 데이터를 직접 수집하고 API를 통해 서버에 연결하면 위치 추적이 가능합니다.
 이 과정에서 GPS에서 수집한 데이터를 처리하기 위해 기존에 존재하는 GPS 회사의 API를 활용할 수 있으며, 이를 소프트웨어에 통합하여 선박의 위치를 실시간으로 추적할 수 있습니다.

---

# VHF를 통한 실시간 정보 수신 및 API 사용 이유

## VHF로 실시간 정보를 받아서 어플리케이션에서 사용하는 방법

### 1. 소프트웨어 정의 라디오(SDR) 준비
- **SDR 장치 선택**: RTL-SDR, HackRF, BladeRF 등의 SDR 장치를 선택합니다.
- **안테나 설치**: VHF 주파수를 수신할 수 있는 안테나를 설치합니다.

### 2. SDR 소프트웨어 설치
- **소프트웨어 선택**: GQRX, GNU Radio, SDR# (SDRSharp) 등의 SDR 소프트웨어를 설치합니다.
- **설정 및 구성**: SDR 소프트웨어를 설정하여 VHF 주파수(161.975 MHz 또는 162.025 MHz)의 AIS 신호를 수신할 수 있도록 구성합니다.

### 3. 신호 수신 및 처리
- **신호 수신**: SDR 장치를 사용하여 VHF 주파수의 AIS 신호를 수신합니다.
- **디지털 신호 변환**: 수신된 신호를 디지털 신호로 변환하고 복호화합니다.
- **데이터 복원**: 변환된 데이터를 통해 원래의 위치, 속도, 항로 등의 정보를 복원합니다.

### 4. 어플리케이션 통합
- **소프트웨어 개발**: SDR 소프트웨어에서 복호화된 데이터를 어플리케이션으로 전송할 수 있도록 소프트웨어를 개발합니다.
- **실시간 데이터 활용**: 어플리케이션에서 실시간으로 수신된 데이터를 활용하여 선박의 위치를 추적하고 정보를 표시합니다.

### 5. 데이터 저장 및 활용
- **수신기 자체 메모리**: VHF 수신기는 내부 메모리를 가지고있어,수신된 데이터를 일시적으로 저장할수 있다.
- **외부 서버**: 수신된 데이터를 외부 서버에 저장. 이 서버는 데이터를 수신하고 저장함. 이 서버에서 데이터를 가져와 처리하는데는 API를 사용함.(대부분의 경우 이 방식을 사용함.) 

## API를 사용하는 이유

### 1. 편의성
- **데이터 수집 및 처리의 간편함**: API를 사용하면 복잡한 신호 처리 과정 없이 정제된 데이터를 쉽게 받아올 수 있습니다.

### 2. 데이터 품질 및 신뢰성
- **검증된 데이터**: API를 통해 제공되는 데이터는 제조사나 데이터 제공업체에서 정제되고 검증된 데이터로, 신호 수신 과정에서 발생할 수 있는 오류를 줄여줍니다.

### 3. 소프트웨어 통합의 용이성
- **다양한 애플리케이션과의 통합**: API는 여러 소프트웨어 애플리케이션과 쉽게 통합될 수 있어 데이터 교환이 원활해집니다.

### 4. 확장성
- **기능 확장**: API를 사용하면 데이터 분석, 보고서 생성, 알림 시스템 등 추가적인 기능을 손쉽게 구현할 수 있습니다.

### 5. 인프라 비용 절감
- **비용 효율성**: 직접 VHF 신호를 수신하고 처리하기 위해 필요한 하드웨어와 소프트웨어 비용을 절감할 수 있습니다.

결론적으로, VHF 신호를 직접 수신하여 어플리케이션에서 실시간 정보를 활용하는 방법도 가능하지만, API를 사용하면 데이터의 신뢰성, 통합의 용이성, 확장성 등에서 더 많은 이점을 제공하는 것을 알 수 있습니다.




즉 AIS는 해양 선박들을 효율적으로 관리하기 위한 시스템일뿐임. 그걸 VHF주파수를 통해 데이터를 가져와서 API로 변환후 데이터를 처리하는것임. 그리고 애초에 GPS에서는 GPS회사들이 관리하기위한 고유의 API를 가지고있음. 그렇다면면 원래는 공홈같은데서 API로 데이터를 수신해왔다면 GPS랑 연결되는 API를 직접 소프트웨어에 연결함으로써 AIS가 공식 사이트에 등록되지 않은경우에도 위치 추적이 가능해짐. 그렇다면 나는 그 API를 가지고 프로그램에 기입할수있게끔 즉 등록할수있게끔하면 된다는거네?


단어:
IMO 번호 (International Maritime Organization) 국제해사기구 등록번호 - 선박마다 부여하는 고유한 일련번호로 7자리 숫자로 이루어지며, 선박의 등록 및 추적에 사용됨.

MMSI 번호(Maritime Mobile Service Identity)해상이동업무식별번호 - AIS 장비는 해상 전화번호라 할 수 있는 고유의 식별번호를 가집니다. MMSI 번호는 9자리 숫자이며 그 중 앞 3자리는 선박의 국가번호를 나타냄.


