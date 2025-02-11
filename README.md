# 목표: 요트 실시간 추적 어플 만들기

지도: dash_deck(추후 구글맵이나 카카오맵으로 변경할예정)
데이터 수신: aisstream.io(AIS)

개발과정
1. ~~대시보드 생성~~  
2. ~~대시보드에 지도 추가~~  
3. ~~모의데이터로 위치정보 표시~~  
4. ~~streamlit sharing 에서 프로그램 배포해서 URL생성~~   
5. ~~aisstream.io에 오픈 API신청~~  
6. ~~오픈 API를 통해 받은 aisstream.io AIS 데이터 편집~~  
7. ~~대시보드 지도에 AIS 위치정보 실시간으로 표시~~  
8. ~~fastapi로 서버 제작~~ --> ~~streamlit에서 dash로 변경~~  
9. ~~정적 데이터 추가, 특정 선박 필터링 기능 추가~~   
10. 요트 분류  
11. 도커를 통한 컨테이너화후 배포  


길이와 넓이로 선박의 유형을 나누는건 가능하지만 요트만 필터링 하는건 유료 api 가 아니면 불가능함.   
공공데이터 포탈에도 등록 현황 통계만 공계할뿐 선박의 자세한 정보는 표기안해주는걸로 봐선 개인정보 보호차원에서 공개 안하는거 같음.  
그렇다면 내가 해야할것 요트만을 선별하는 수식 구현

---

##국제 해양법: 선박의 길이와 폭에 따라 크기 분류.

소형 선박: 길이가 20미터 이하, 폭 6미터 이하

중형 선박: 길이가 20미터 ~ 50미터,폭이 6미터 ~ 15미터

대형 선박: 50미터 이상, 폭 15미터 이상

---

##선박 분류 타입 번호

| shipTypeCode | shipTypeDescription                                      | shipType             |
|-------------|---------------------------------------------------------|----------------------|
| 20          | Wing in ground (WIG), all ships of this type             | OTHER               |
| 21          | Wing in ground (WIG), Hazardous category A               | OTHER               |
| 22          | Wing in ground (WIG), Hazardous category B               | OTHER               |
| 23          | Wing in ground (WIG), Hazardous category C               | OTHER               |
| 24          | Wing in ground (WIG), Hazardous category D               | OTHER               |
| 25          | Wing in ground (WIG), Reserved for future use            | OTHER               |
| 26          | Wing in ground (WIG), Reserved for future use            | OTHER               |
| 27          | Wing in ground (WIG), Reserved for future use            | OTHER               |
| 28          | Wing in ground (WIG), Reserved for future use            | OTHER               |
| 29          | Wing in ground (WIG), Reserved for future use            | OTHER               |
| 30          | Fishing                                                 | FISHING             |
| 31          | Towing                                                  | TUG                 |
| 32          | Towing                                                  | TUG                 |
| 33          | Dredging or underwater ops                              | DREDGER             |
| 34          | Diving ops                                              | DIVE_VESSEL         |
| 35          | Military Ops                                           | MILITARY_OPS        |
| 📌36          | Sailing                                                | SAILING             |
| 📌37          | Pleasure Craft                                         | PLEASURE_CRAFT      |
| 38          | Reserved                                               | OTHER               |
| 39          | Reserved                                               | OTHER               |
| 40          | High speed craft (HSC), all ships of this type         | HIGH_SPEED_CRAFT    |
| 41          | High speed craft (HSC), Hazardous category A           | HIGH_SPEED_CRAFT    |
| 42          | High speed craft (HSC), Hazardous category B           | HIGH_SPEED_CRAFT    |
| 43          | High speed craft (HSC), Hazardous category C           | HIGH_SPEED_CRAFT    |
| 44          | High speed craft (HSC), Hazardous category D           | HIGH_SPEED_CRAFT    |
| 45          | High speed craft (HSC), Reserved for future use        | HIGH_SPEED_CRAFT    |
| 46          | High speed craft (HSC), Reserved for future use        | HIGH_SPEED_CRAFT    |
| 47          | High speed craft (HSC), Reserved for future use        | HIGH_SPEED_CRAFT    |
| 48          | High speed craft (HSC), Reserved for future use        | HIGH_SPEED_CRAFT    |
| 49          | High speed craft (HSC), No additional information      | HIGH_SPEED_CRAFT    |
| 50          | Pilot Vessel                                           | PILOT_VESSEL        |
| 51          | Search and Rescue vessel                               | SEARCH_AND_RESCUE   |
| 52          | Tug                                                    | TUG                 |
| 53          | Port Tender                                            | PORT_TENDER         |
| 54          | Anti-pollution equipment                               | ANTI_POLLUTION      |
| 55          | Law Enforcement                                        | LAW_ENFORCEMENT     |
| 56          | Spare – Local Vessel                                   | OTHER               |
| 57          | Spare – Local Vessel                                   | OTHER               |
| 58          | Medical Transport                                      | MEDICAL_TRANS       |
| 59          | Noncombatant ship according to RR Resolution No. 18    | SPECIAL_CRAFT       |
| 60          | Passenger, all ships of this type                      | PASSENGER           |
| 61          | Passenger, Hazardous category A                        | PASSENGER           |
| 62          | Passenger, Hazardous category B                        | PASSENGER           |
| 63          | Passenger, Hazardous category C                        | PASSENGER           |
| 64          | Passenger, Hazardous category D                        | PASSENGER           |
| 65          | Passenger, Reserved for future use                     | PASSENGER           |
| 66          | Passenger, Reserved for future use                     | PASSENGER           |
| 67          | Passenger, Reserved for future use                     | PASSENGER           |
| 68          | Passenger, Reserved for future use                     | PASSENGER           |
| 69          | Passenger, No additional information                   | PASSENGER           |
| 70          | Cargo, all ships of this type                          | GENERAL_CARGO       |
| 71          | Cargo, Hazardous category A                            | GENERAL_CARGO       |
| 72          | Cargo, Hazardous category B                            | GENERAL_CARGO       |
| 73          | Cargo, Hazardous category C                            | GENERAL_CARGO       |
| 74          | Cargo, Hazardous category D                            | GENERAL_CARGO       |
| 75          | Cargo, Reserved for future use                         | GENERAL_CARGO       |
| 76          | Cargo, Reserved for future use                         | GENERAL_CARGO       |
| 77          | Cargo, Reserved for future use                         | GENERAL_CARGO       |
| 78          | Cargo, Reserved for future use                         | GENERAL_CARGO       |
| 79          | Cargo, No additional information                       | GENERAL_CARGO       |
| 80          | Tanker, all ships of this type                         | GENERAL_TANKER      |
| 81          | Tanker, Hazardous category A                           | GENERAL_TANKER      |
| 82          | Tanker, Hazardous category B                           | GENERAL_TANKER      |
| 83          | Tanker, Hazardous category C                           | GENERAL_TANKER      |
| 84          | Tanker, Hazardous category D                           | GENERAL_TANKER      |
| 85          | Tanker, Reserved for future use                        | GENERAL_TANKER      |
| 86          | Tanker, Reserved for future use                        | GENERAL_TANKER      |
| 87          | Tanker, Reserved for future use                        | GENERAL_TANKER      |
| 88          | Tanker, Reserved for future use                        | GENERAL_TANKER      |
| 89          | Tanker, No additional information                      | GENERAL_TANKER      |
| 90          | Other Type, all ships of this type                     | OTHER               |
| 91          | Other Type, Hazardous category A                       | OTHER               |
| 92          | Other Type, Hazardous category B                       | OTHER               |
| 93          | Other Type, Hazardous category C                       | OTHER               |
| 94          | Other Type, Hazardous category D                       | OTHER               |
| 95          | Other Type, Reserved for future use                    | OTHER               |
| 96          | Other Type, Reserved for future use                    | OTHER               |
| 97          | Other Type, Reserved for future use                    | OTHER               |
| 98          | Other Type, Reserved for future use                    | OTHER               |
| 99          | Other Type, no additional information                   | OTHER               |

---

웹소켓이 란?
양방향 통신: 클라이언트(예: 웹 브라우저)와 서버가 서로 데이터를 주고받을 수 있습니다. 한쪽에서 데이터를 보내면 실시간으로 다른 쪽에서 바로 받을 수 있습니다.  

지속적인 연결: 일반적인 HTTP 요청과 달리, 웹소켓 연결은 한번 열리면 클라이언트와 서버 간의 지속적인 연결이 유지됩니다. 이로 인해 실시간 데이터 업데이트가 가능합니다.  

낮은 오버헤드: 기존의 HTTP 요청에 비해 데이터 전송 시 헤더가 적어 오버헤드가 낮습니다. 따라서 실시간 데이터를 더 효율적으로 주고받을 수 있습니다.  

MMSI를 입력해서 해당 선박의 위치 데이터만 따로 표시가능

---

##요트는 AIS 송출 받기가 어려움.
개인 요트는 AIS 송출이 법적으로 의무화되있지 않음.  
AIS 송출이 의무화되있는건 상업용 선박의 경우에만해당됨.  
따라서 대부분의 요트들은 AIS를 꺼놓음.  

상업용으로 등록되있는 요트들의 AIS 송출이 없는 경우  
1. 사업자들이 일부러 AIS를 끄는 경우  
2. 개인 정보 보호 & 보안 이유  

VIP 고객(연예인, 기업인 등)의 위치 노출을 막기 위해 AIS를 끄는 경우가 많음  
특히 고급 요트 대여 업체는 고객 프라이버시 보호를 강조하는 경우가 많음  
AIS 데이터를 공개하면 운항 루트 & 위치가 실시간으로 노출되기 때문  
✅ 국내 법적 허점 (단거리 운항 시 AIS 의무가 없음.)  

국제항해를 하지 않는 요트는 AIS 송출 의무가 느슨함.  
특히 내수면(강, 한강 등)이나 해안가에서 단거리 운항하는 경우 AIS 필요 없음  
단거리 대여 위주로 운영하는 업체들은 AIS를 꺼놓고 운항할 가능성이 큼  
필요할 때만 AIS를 켜는 방식으로 운영  