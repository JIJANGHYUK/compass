try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("이 코드는 streamlit 패키지가 필요합니다. 'pip install streamlit'으로 설치하세요.")

# 건물 정보 입력
st.sidebar.markdown("**층수 정보**")
floors_above = st.sidebar.number_input("지상 층수", min_value=0)
floors_below = st.sidebar.number_input("지하 층수", min_value=0)
st.sidebar.title("건물 정보 입력")
building_type = st.sidebar.selectbox("건물 용도", [
    "공동주택", "문화 및 집회시설", "운동시설", "업무시설", "근린생활시설",
    "판매시설", "의료시설", "숙박시설", "위락시설", "교육연구시설",
    "노유자시설", "수련시설", "운수시설", "창고시설", "공장",
    "위험물 저장 및 처리시설", "자동차 관련시설", "동물 및 식물 관련시설", "분뇨 및 쓰레기처리시설",
    "교정 및 군사시설", "방송통신시설", "발전시설", "묘지 관련시설", "관광휴게시설",
    "장례시설", "종교시설", "기타시설", "복합건축물", "건설현장", "지하도상가"
])
area = st.sidebar.number_input("연면적 (㎡)", min_value=0)
floors = st.sidebar.number_input("층수", min_value=1)
has_basement = st.sidebar.checkbox("지하 있음")
has_it_room = st.sidebar.checkbox("전산실/통신실 있음")
has_gas = st.sidebar.checkbox("가스설비 있음")
approval_date = st.sidebar.date_input("사용승인일")

# 추가 입력 항목
has_windowless_floor = st.sidebar.checkbox("무창층 있음")
has_floor_over_600 = st.sidebar.checkbox("600㎡ 이상인 층 있음")
tunnel_length = st.sidebar.number_input("터널 길이 (m)", min_value=0)
is_designated_tunnel = st.sidebar.checkbox("지정된 터널 여부")
sub_type = st.sidebar.text_input("세부 용도 (예: 고시원, 산후조리원 등)")
basement_area = st.sidebar.number_input("지하층 연면적 (㎡)", min_value=0)
layered_use = st.sidebar.checkbox("용도별 층 분리 필요")
has_auto_suppression_alt = st.sidebar.checkbox("자동소화설비로 대체 여부")
occupancy = st.sidebar.number_input("수용 인원 (명)", min_value=0)

# 결과 표시
st.title("소방시설 설치 기준 자동 조회")
st.write("입력한 건물 정보에 따라 필요한 소방시설 내역을 확인해보세요.")
st.markdown("<p style='font-size:13px;'>※ 법령 출처: <a href='https://www.law.go.kr/lbook/lbInfoR.do?lbookSeq=100443' target='_blank'>소방시설법령집 국가법령정보센터</a></p>", unsafe_allow_html=True)

# 설비별 조건 로직 시작
from collections import defaultdict
from datetime import date

def get_fire_facilities(building_type, area, floors,
                        has_basement, has_it_room, has_gas, approval_date, sub_type, basement_area, layered_use, has_auto_suppression_alt, occupancy, has_windowless_floor, has_floor_over_600, tunnel_length, is_designated_tunnel):
    categorized = defaultdict(list)

    def add(category, name, required, desc, law_text):
        categorized[category].append({
            "name": name,
            "required": required,
            "desc": desc,
            "law_text": law_text
        })

    # 조견표 기준 적용 예시 (1차: 소화설비 일부)

    # ✅ 소화기구
    add("소화설비", "소화기구", area >= 33, "연면적 33㎡ 이상 모든 건축물은 소화기구를 설치해야 합니다.", "소방시설법 시행령 제15조")

    # ✅ 옥내소화전설비
    add("소화설비", "옥내소화전설비", (
        (sub_type in ["옥상차고", "지하주차장"] and area >= 200)
        or (sub_type == "터널" and tunnel_length >= 1000)
        or is_designated_tunnel
        or (area >= 3000 and sub_type != "터널")
        or ((has_basement or has_windowless_floor or floors >= 4) and has_floor_over_600)
    ), "옥상차고·지하주차장 200㎡ 이상, 지하가·터널 1000㎡ 이상, 연면적 3000㎡ 이상, 무창층·4층 이상 중 바닥 600㎡ 이상 층 포함 시 설치.", "소방시설법 시행령 제15조")

    # ✅ 옥외소화전설비
    add("소화설비", "옥외소화전설비", (
        (sub_type == "목조건축물" and approval_date.year < 2000) or
        (floors <= 2 and area >= 9000)
    ), "보물·국보급 목조건축물 또는 지상 1~2층 바닥면적 합계가 9000㎡ 이상인 경우 설치.", "소방시설법 시행령 제15조")

    # ✅ 스프링클러설비
    add("소화설비", "스프링클러설비", (
        not has_auto_suppression_alt and (
            (floors >= 6)
            or (building_type in ["수련시설", "교육연구시설"] and sub_type == "기숙사" and area >= 5000)
            or (building_type == "문화 및 집회시설" and occupancy >= 100)
            or (building_type == "영화상영관" and ((has_basement or has_windowless_floor) and area >= 500 or area >= 1000))
            or (sub_type == "무대부" and ((has_basement or has_windowless_floor or floors >= 4) and area >= 300 or area >= 500))
            or (building_type in ["판매시설", "운수시설", "창고시설"] and (area >= 5000 or occupancy >= 500))
            or (building_type in ["근린생활시설", "의료시설", "노유자시설", "수련시설", "숙박시설"] and area >= 600)
            or (building_type == "교육연구시설" and area >= 5000)
            or (building_type == "운동시설" and occupancy >= 100)
            or (building_type in ["업무시설", "위락시설"] and area >= 600)
            or (sub_type == "랙식창고" and st.sidebar.number_input("랙식창고 층 높이 (m)", min_value=0) > 10 and area >= 1500)
            or (building_type in ["공장", "창고시설"] and st.sidebar.checkbox("특수가연물 1000배 이상 저장 여부"))
            or (building_type in ["공장", "창고시설"] and not st.sidebar.checkbox("불연재료 외벽 여부") and area >= 2500)
            or (sub_type in ["보호감호소", "교도소", "유치장"])
            or (building_type == "지하도상가" and area >= 1000)
            or (building_type == "발전시설" and sub_type == "전기저장시설")
        )
    ), "스프링클러설비는 층수, 연면적, 용도 및 특수조건에 따라 다양한 기준에 의해 설치가 요구됩니다.", "소방시설법 시행령 제15조")

    # ✅ 자동화재탐지설비

    # ✅ 비상방송설비
    add("경보설비", "비상방송설비", (
        (
            area >= 3500
            or (floors_below >= 3)
            or (floors_above >= 11)
        )
        and building_type not in [
            "위험물 저장 및 처리시설",
            "동물 및 식물 관련시설",
            "지하구",
            "지하도상가"
        ]
        and sub_type != "터널"
    ), "연면적 3,500㎡ 이상, 지하 3층 이상, 지상 11층 이상인 건축물로 특정 제외 대상이 아닌 경우 설치.", "소방시설법 시행령 제15조")
    add("경보설비", "비상방송설비", (
        (
            area >= 3500
            or (has_basement and floors >= 3)
            or (floors >= 11)
        )
        and building_type not in [
            "위험물 저장 및 처리시설",
            "동물 및 식물 관련시설",
            "지하구",
            "지하도상가"
        ]
        and sub_type != "터널"
    ), "연면적 3,500㎡ 이상, 지하 3층 이상, 11층 이상인 건축물로 특정 제외 대상이 아닌 경우 설치.", "소방시설법 시행령 제15조")

    # ✅ 비상경보설비

    # ✅ 누전경보기

    # ✅ 자동화재속보설비

    # ✅ 단독경보형감지기

    # ✅ 시각경보기

    # ✅ 가스누설경보기
    add("경보설비", "가스누설경보기", (
        building_type in [
            "문화 및 집회시설", "종교시설", "판매시설", "운수시설",
            "의료시설", "노유자시설", "수련시설", "운동시설",
            "숙박시설", "장례시설"
        ]
        or (building_type == "창고시설" and sub_type == "물류터미널")
    ), "가스를 사용하는 시설 중 특정 용도에 해당하면 가스누설경보기 설치 필요.", "소방시설법 시행령 제15조")
    add("경보설비", "시각경보기", (
        building_type in [
            "근린생활시설", "문화 및 집회시설", "종교시설", "판매시설",
            "운수시설", "의료시설", "노유자시설", "운동시설",
            "업무시설", "숙박시설", "위락시설", "발전시설",
            "장례시설"
        ]
        or (building_type == "교육연구시설" and sub_type == "도서관")
        or (building_type == "방송통신시설" and sub_type == "방송국")
        or (building_type == "창고시설" and sub_type == "물류터미널")
        or (building_type == "지하도상가")
    ), "청각장애인을 위한 경보시설로서 특정 용도에 설치 필요.", "소방시설법 시행령 제15조")
    add("경보설비", "단독경보형감지기", (
        (building_type == "공동주택" and sub_type in ["연립주택", "다세대주택"])
        or (building_type in ["교육연구시설", "수련시설"] and sub_type in ["기숙사", "합숙소"] and area < 2000)
        or (building_type == "유치원" and area < 400)
        or (building_type == "노유자시설" and area >= 400)
        or (building_type == "수련시설" and st.sidebar.checkbox("숙박기능 있음") and area >= 400 and occupancy < 100)
    ), "공동주택(연립·다세대), 유치원·기숙사·합숙소 등 2000㎡ 미만, 400㎡ 이상 노유자·수련시설 중 일부 조건에 해당 시 설치.", "소방시설법 시행령 제15조")
    add("경보설비", "자동화재속보설비", (
        sub_type in ["조산원", "산후조리원"]
        or (building_type == "판매시설" and sub_type == "전통시장")
        or (building_type == "근린생활시설" and sub_type in ["의원", "치과의원", "한의원"] and st.sidebar.checkbox("입원실 있음"))
        or (building_type == "의료시설" and sub_type in ["종합병원", "병원", "치과병원", "한방병원", "요양병원"])
        or (building_type == "의료시설" and sub_type in ["정신병원", "의료재활시설"] and has_floor_over_600)
        or (building_type == "노유자시설")
        or (building_type in ["노유자시설", "수련시설"] and has_floor_over_600 and st.sidebar.checkbox("숙박기능 있음"))
        or (building_type == "지하구")
        or (sub_type == "목조건축물" and approval_date.year < 2000)
    ), "조산원, 산후조리원, 전통시장, 입원실 있는 의원 등, 정신병동·노유자시설 등 특정 조건 시 설치.", "소방시설법 시행령 제15조")
    contract_current = st.sidebar.number_input("계약 전류용량 (A)", min_value=0)
    add("경보설비", "누전경보기", (
        contract_current > 100
        and building_type not in ["위험물 저장 및 처리시설", "동물 및 식물 관련시설", "지하구"]
        and sub_type != "터널"
    ), "계약전류용량이 100A를 초과하고, 특정 제외시설이 아닌 경우 설치.", "소방시설법 시행령 제15조")
    add("경보설비", "비상경보설비", (
        (occupancy >= 50 and sub_type == "옥내작업장")
        or ((has_basement or has_windowless_floor) and area >= (100 if sub_type == "공연장" else 150))
        or (area >= 400 and building_type not in ["공장", "창고시설", "위험물 저장 및 처리시설", "동물 및 식물 관련시설", "지하구"])
        or (sub_type == "터널" and tunnel_length >= 500)
    ), "50명 이상 근로자의 옥내작업장, 지하/무창층 150㎡ 이상(공연장은 100㎡), 연면적 400㎡ 이상(일부 시설 제외), 터널 500m 이상 등 조건에 해당 시 설치.", "소방시설법 시행령 제15조")
    add("경보설비", "자동화재탐지설비", (
        (building_type == "공동주택" and sub_type in ["아파트", "기숙사"])
        or (building_type == "근린생활시설" and (area >= 600 or sub_type == "목욕장" and area >= 1000 or sub_type in ["조산원", "산후조리원"]))
        or (building_type in ["문화 및 집회시설", "종교시설", "판매시설", "운수시설"] and area >= 1000)
        or (floors >= 6 and building_type in ["문화 및 집회시설", "종교시설", "판매시설", "운수시설"])
        or (building_type == "판매시설" and sub_type == "전통시장")
        or (building_type == "의료시설" and (area >= 600 or (sub_type == "정신의료기관" and (area >= 300 or st.sidebar.checkbox("정신병동 창살 있음")))))
        or (building_type == "교육연구시설" and area >= 2000)
        or (building_type == "노유자시설" and area >= 400)
        or (building_type == "수련시설" and (area >= 2000 or occupancy >= 100))
        or (building_type in ["운동시설", "업무시설"] and area >= 1000)
        or (building_type == "숙박시설")
        or (building_type == "위락시설" and area >= 600)
        or (building_type in ["공장", "창고시설", "위험물 저장 및 처리시설", "자동차 관련시설"] and area >= 1000)
        or (building_type in ["동물 및 식물 관련시설", "분뇨 및 쓰레기처리시설", "교정 및 군사시설"] and area >= 2000)
        or (building_type in ["방송통신시설", "발전시설"] and area >= 1000)
        or (building_type == "묘지 관련시설" and area >= 2000)
        or (building_type == "관광휴게시설" and area >= 1000)
        or (building_type == "장례시설" and area >= 600)
        or (building_type == "지하도상가" and area >= 1000)
        or (sub_type == "터널" and tunnel_length >= 1000)
        or (building_type == "복합건축물" and area >= 600)
    ), "조견표 기준에 따라 건축물 용도, 층수, 연면적 등에 따라 자동화재탐지설비 설치.", "소방시설법 시행령 제15조")

    # ✅ 물분무등소화설비

    # ✅ 제연설비

    # ✅ 연결송수관설비

    # ✅ 비상콘센트설비

    # ✅ 무선통신보조설비

    # ✅ 연소방지설비
    add("소화활동설비", "연소방지설비", (
        (building_type == "지하구" and sub_type in ["전력시설", "통신시설"])
        or (floors >= 50 and area >= 0 and st.sidebar.number_input("건물 높이 (m)", min_value=0) >= 200)
        or (floors >= 11 and occupancy >= 5000 and st.sidebar.checkbox("지하역사 또는 지하상가와 연결됨"))
    ), "지하구(전력·통신용), 50층 이상 + 200m 이상 건물, 11층 이상 + 1일 수용인원 5000명 이상 + 지하연결 시 연소방지설비 설치.", "소방시설법 시행령 제15조")
    add("소화활동설비", "무선통신보조설비", (
        (
            (floors_above >= 30)
            or (sub_type == "터널" and tunnel_length >= 500)
            or (building_type == "지하도상가" and area >= 1000)
            or (floors_below >= 3 and basement_area >= 1000)
            or (basement_area >= 3000)
        )
        or (building_type == "지하구" and sub_type == "공동구")
    ), "30층 이상, 터널 500m 이상, 지하상가 1000㎡ 이상, 지하층 3개 이상 + 1000㎡ 이상, 지하층 3000㎡ 이상 또는 공동구일 경우 무선통신보조설비 설치.", "소방시설법 시행령 제15조")
    add("소화활동설비", "비상콘센트설비", (
        (
            (floors_above >= 11)
            or (sub_type == "터널" and tunnel_length >= 500)
            or (has_basement and floors >= 3 and basement_area >= 1000)
        )
        and building_type != "위험물 저장 및 처리시설"
        and sub_type != "가스시설"
        and building_type != "지하구"
    ), "11층 이상, 터널 500m 이상, 지하 3개층 이상 + 지하층 합계 1000㎡ 이상이면 해당 층에 설치. 일부 시설 제외.", "소방시설법 시행령 제15조")
    add("소화활동설비", "연결송수관설비", (
        (
            (floors_above >= 5 and area >= 6000)
            or (floors_above + floors_below >= 7)
            or (has_basement and floors >= 3 and basement_area >= 1000)
            or (sub_type == "터널" and tunnel_length >= 1000)
        )
        and building_type != "위험물 저장 및 처리시설"
        and sub_type != "가스시설"
        and building_type != "지하구"
    ), "5층 이상 + 연면적 6000㎡ 이상, 지하 포함 7개층 이상, 지하 3층 이상 + 지하면적 1000㎡ 이상, 터널 1000m 이상일 경우 설치. 일부 시설 제외.", "소방시설법 시행령 제15조")

    # ✅ 연결살수설비
    gas_tank_volume = st.sidebar.number_input("노출된 가스탱크 용량 (톤)", min_value=0)
    add("소화활동설비", "연결살수설비", (
        (has_basement and area >= 150)
        or (building_type == "공동주택" and sub_type == "국민주택규모이하아파트" and has_basement)
        or (building_type == "교육연구시설" and has_basement and area >= 700)
        or (building_type in ["판매시설", "운수시설"] and area >= 1000)
        or (building_type == "창고시설" and sub_type == "물류터미널" and area >= 1000)
        or (gas_tank_volume >= 30)
    ), "지하층 150㎡ 이상, 국민주택규모 아파트 지하, 학교 지하 700㎡ 이상, 대형 판매·운수·물류시설, 가스탱크 30톤 이상이면 설치.", "소방시설법 시행령 제15조")
    add("소화활동설비", "제연설비", (
        (sub_type == "행정안전부령터널")
        or (building_type in ["문화 및 집회시설", "종교시설", "운동시설"] and area >= 200)
        or (building_type == "영화상영관" and occupancy >= 100)
        or (building_type == "지하도상가" and area >= 1000)
        or (has_basement and floors >= 5 and area >= 3000)
        or (sub_type in ["특별피난계단", "비상용승강기승강장", "피난용승강기승강장"] and building_type != "공동주택")
        or ((has_basement or has_windowless_floor) and area >= 1000 and building_type in [
            "근린생활시설", "판매시설", "운수시설", "숙박시설", "위락시설",
            "의료시설", "노유자시설", "창고시설"
        ] and sub_type == "물류터미널")
        or (building_type == "운수시설" and sub_type in ["시외버스정류장", "철도시설", "도시철도시설", "공항시설", "항만시설"] and (has_basement or has_windowless_floor) and area >= 1000)
    ), "터널, 대공간 문화시설, 100명 이상 영화관, 대형 지하공간, 피난 승강장, 지하층·무창층에 있는 특정 용도 시설에 설치.", "소방시설법 시행령 제15조")

    # ✅ 소화용수설비
    add("소화용수설비", "소화용수설비", (
        (area >= 5000 and building_type not in ["위험물 저장 및 처리시설", "동물 및 식물 관련시설", "지하구"] and sub_type != "터널")
        or (building_type == "위험물 저장 및 처리시설" and has_gas and st.sidebar.number_input("노출된 가스탱크 저장용량 합계 (톤)", min_value=0) >= 100)
        or (building_type == "분뇨 및 쓰레기처리시설" and sub_type in ["폐기물 재활용 시설", "폐기물 처분시설"])
    ), "연면적 5000㎡ 이상(일부 제외), 노출탱크 가스시설 100톤 이상, 폐기물 재활용·처분시설 등은 소화용수설비 설치.", "소방시설법 시행령 제15조")
    add("소화설비", "물분무등소화설비", (
        (sub_type == "항공기격납고")
        or (sub_type == "기계식주차시설" and occupancy >= 20)
        or (sub_type in ["차고", "주차장"] and area >= 200)
        or (sub_type in ["전기실", "발전실", "변전실", "축전지실", "통신기기실", "전산실"] and area >= 300)
        or (sub_type in ["차고주차용건축물", "주차시설"] and area >= 800)
        or (sub_type == "지정문화재")
        or (sub_type == "행정안전부령터널")
        or (sub_type == "방사성폐기물저장시설" and st.sidebar.checkbox("소화수처리설비 없음"))
    ), "항공기격납고, 20대 이상 기계식주차시설, 차고·주차장 200㎡ 이상, 전기·통신 관련실 300㎡ 이상, 주차시설 800㎡ 이상, 지정문화재, 방사성폐기물저장시설 등 조건 해당 시 설치.", "소방시설법 시행령 제15조")

    # ✅ 간이스프링클러설비

    # ✅ 피난기구

    # ✅ 휴대용비상조명등
    add("피난구조설비", "휴대용비상조명등", (
        building_type == "숙박시설"
        or sub_type == "다중이용업소"
        or (occupancy >= 100 and sub_type in ["영화상영관", "대규모점포", "지하역사", "지하상가"])
    ), "숙박시설, 다중이용업소, 수용인원 100명 이상 영화상영관·대규모점포·지하역사·지하상가 등에 설치.", "소방시설법 시행령 제15조")

    # ✅ 비상조명등
    add("피난구조설비", "비상조명등", (
        ((has_basement or has_windowless_floor) and area >= 450)
        or (sub_type == "터널" and tunnel_length >= 500)
        or (has_basement and floors >= 5 and area >= 3000)
    ) and building_type not in ["창고시설", "하역장", "위험물 저장 및 처리시설"] and sub_type != "가스시설",
    "지하층·무창층 450㎡ 이상, 터널 500m 이상, 5개층 이상 + 3000㎡ 이상인 경우 설치. 창고·하역장·가스시설 제외.", "소방시설법 시행령 제15조")

    # ✅ 인명구조기구

    # ✅ 피난유도등 및 유도표지
    add("피난구조설비", "피난유도등 및 유도표지", (
        building_type not in ["동물 및 식물 관련시설", "지하구"] and sub_type != "터널"
    ), "모든 특정소방대상물에 설치. 단, 지하가 중 터널 및 동물·식물 관련 축사, 지하구는 제외.", "소방시설법 시행령 제15조")

    # ✅ 객석유도등
    add("피난구조설비", "객석유도등", (
        (sub_type in ["카바레", "나이트클럽"])
        or building_type in ["문화 및 집회시설", "종교시설", "운동시설"]
    ), "유흥주점 및 문화·종교·운동시설의 객석에 설치.", "소방시설법 시행령 제15조")

    # ✅ 피난유도선
    add("피난구조설비", "피난유도선", (
        sub_type == "다중이용업소" and (st.sidebar.checkbox("피난통로 폭 120cm 이상") or st.sidebar.checkbox("복도 폭 150cm 이상 및 열리는 방향"))
    ), "다중이용업소 내 피난통로 또는 복도가 일정 폭 이상일 경우 설치.", "소방시설법 시행령 제15조")
    add("피난구조설비", "인명구조기구", (
        (building_type == "의료시설" and (floors + (1 if has_basement else 0)) >= 5)
        or (building_type == "숙박시설" and sub_type == "관광호텔" and (floors + (1 if has_basement else 0)) >= 7)
        or (
            occupancy >= 100 and sub_type in [
                "영화상영관", "대규모점포", "지하역사", "지하상가"
            ]
        )
        or (sub_type == "이산화탄소소화설비" and sub_type != "호스릴 이산화탄소 소화설비")
    ), "병원 5개층 이상, 관광호텔 7개층 이상, 수용인원 100명 이상 대형시설, 이산화탄소소화설비 적용 대상 등은 인명구조기구 필요.", "소방시설법 시행령 제15조")
    add("피난구조설비", "피난기구", (
        (floors not in [1, 2] and floors < 11 and not st.sidebar.checkbox("피난층 여부"))
        or (building_type == "노유자시설" and floors in [1, 2] and not st.sidebar.checkbox("피난층 여부"))
    ) and building_type not in ["위험물 저장 및 처리시설", "동물 및 식물 관련시설", "지하구"] and sub_type != "가스시설" and sub_type != "터널",
    "피난층, 지상 1층·2층 및 11층 이상을 제외한 층, 노유자시설의 특정 층 외에 설치. 위험물(가스), 지하구, 터널 제외.", "소방시설법 시행령 제15조")
    add("소화설비", "간이스프링클러설비", (
        (sub_type in ["연립주택", "다세대주택"] and area >= 100)
        or (building_type == "교육연구시설" and sub_type == "합숙소" and area >= 100)
        or (building_type == "노유자시설" and area >= 300 and area < 600)
        or (building_type == "의료시설" and sub_type in ["정신의료기관", "의료재활시설", "노유자시설로 사용하는 숙박시설"] and (
            (area >= 300 and area < 600) or (area < 300 and st.sidebar.checkbox("창살 설치됨"))
        ))
        or (sub_type in ["조산원", "산후조리원"] and area < 600)
        or (sub_type in ["종합병원", "병원", "치과병원", "한방병원", "요양병원"] and area < 600)
        or (building_type == "근린생활시설" and area >= 1000)
        or (building_type == "복합건축물" and area >= 1000)
        or (sub_type in ["의원", "치과의원", "한의원"] and st.sidebar.checkbox("입원실 있음"))
        or (sub_type in ["출입구보호시설", "다중이용업소의 지하층", "고시원", "산후조리원", "실내권총사격장"])
    ), "조견표 기준에 따라 간이스프링클러설비가 필요한 경우에 해당.", "소방시설법 시행령 제15조")
    

    return categorized

results = get_fire_facilities(
    building_type, area, floors_above + floors_below,
    has_basement, has_it_room, has_gas, approval_date, sub_type,
    basement_area, layered_use, has_auto_suppression_alt, occupancy,
    has_windowless_floor, has_floor_over_600, tunnel_length, is_designated_tunnel
)

for category, items in results.items():
    st.subheader(f"📂 {category}")
    cols = st.columns(2)
    for i, r in enumerate(items):
        with cols[i % 2]:
            if r['required'] is True:
                symbol = '✅'
                label = '필요'
            elif r['required'] is False:
                symbol = '⚠️'
                label = '선택'
            else:
                symbol = '❌'
                label = '해당없음'

            st.markdown(f"""
            <div style='background-color:#f9f9f9; padding:12px 16px; border-radius:10px; margin-bottom:16px; box-shadow: 0 0 3px rgba(0,0,0,0.05);'>
              <div style='font-size:20px; font-weight:600;'>{symbol} {r['name']}</div>
              <div style='margin-top:6px; font-size:14px;'>
                <b>설치 여부:</b> {label}<br>
                <b>설명:</b> {r['desc']}<br>
                <b>관련 기준/법령 설명:</b> {r['law_text']}
              </div>
            </div>
            """, unsafe_allow_html=True)
