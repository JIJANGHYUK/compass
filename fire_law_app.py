try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("이 코드는 streamlit 패키지가 필요합니다. 'pip install streamlit'으로 설치하세요.")

# 건물 정보 입력
st.sidebar.title("건물 정보 입력")
building_type = st.sidebar.selectbox("건물 용도", [
    "공동주택", "근린생활시설", "공장", "복합건축물", "창고시설",
    "교육연구시설", "지하상가", "역사", "업무시설", "건설현장",
    "숙박시설", "노유자시설", "기숙사", "의료시설", "전산실"
])
area = st.sidebar.number_input("연면적 (㎡)", min_value=0)
floors = st.sidebar.number_input("층수", min_value=1)
has_basement = st.sidebar.checkbox("지하 있음")
has_it_room = st.sidebar.checkbox("전산실/통신실 있음")
has_gas = st.sidebar.checkbox("가스설비 있음")
approval_date = st.sidebar.date_input("사용승인일")

# 추가 입력 항목
sub_type = st.sidebar.text_input("세부 용도 (예: 고시원, 산후조리원 등)")
basement_area = st.sidebar.number_input("지하층 연면적 (㎡)", min_value=0)
layered_use = st.sidebar.checkbox("용도별 층 분리 필요")
has_auto_suppression_alt = st.sidebar.checkbox("자동소화설비로 대체 여부")
occupancy = st.sidebar.number_input("수용 인원 (명)", min_value=0)

# 소방시설 판단 함수 예시 구조 (이후 확장 가능)
def get_fire_facilities(building_type, area, floors, has_basement, has_it_room, has_gas, occupancy, approval_date, sub_type, basement_area, layered_use, has_auto_suppression_alt):
    from datetime import date
    from collections import defaultdict
    categorized = defaultdict(list)

    def add(category, name, required, desc, law_text, law_link):
        categorized[category].append({
            "name": name,
            "required": required,
            "desc": desc,
            "law_text": law_text,
            "law_link": law_link
        })

    law_center_link = "https://www.law.go.kr/lbook/lbInfoR.do?lbookSeq=100443"

    # 소화설비
    add("소화설비", "소화기,자동확산소화기", area >= 33, "연면적 33㎡ 이상이면 소화기 설치 필요.", "시행령 제15조", law_center_link)
    add("소화설비", "자동소화장치", None, "기계실 등 위험구역 또는 특정 설비에 설치.", "시행령 제15조", law_center_link)
    add("소화설비", "옥내소화전설비", area >= 1000, "연면적 1000㎡ 이상일 경우 설치.", "시행령 제15조", law_center_link)
    add("소화설비", "스프링클러설비", (
        not has_auto_suppression_alt and (
            (building_type == "공동주택" and floors >= 11)
            or (building_type == "노유자시설" and area >= 600 and approval_date >= date(2018, 6, 26))
        )
    ), "공동주택 11층 이상 또는 노유자시설 중 일정 조건에 해당.", "시행령 제15조", law_center_link)
    add("소화설비", "간이스프링클러설비", (
        building_type == "근린생활시설" and sub_type in ["고시원", "산후조리원"] and area >= 600
    ), "고시원 또는 산후조리원 등 일정 조건의 근린생활시설에서 600㎡ 이상이면 설치 대상.", "시행령 제15조", law_center_link)

    add("소화설비", "가스소화설비(이산화탄소, 할론)", has_it_room, "전산실/통신실 등 특정 장소에만 설치.", "시행령 제15조", law_center_link)
    add("소화설비", "옥외소화전설비", area >= 1000, "옥외 대형 대응이 필요한 경우 설치.", "시행령 제15조", law_center_link)

    # 경보설비
    add("경보설비", "비상경보설비", area >= 400, "특정 용도 및 연면적 기준 이상일 경우 설치.", "시행령 제13조", law_center_link)
    add("경보설비", "자동화재탐지설비 및 시각경보기", area >= 400 or has_basement, "지하 포함 건물 및 연면적 400㎡ 이상인 경우 설치.", "시행령 제13조", law_center_link)
    add("경보설비", "비상방송설비", building_type in ["숙박시설", "노유자시설"], "숙박 및 노유자시설 등에 설치.", "시행령 제13조", law_center_link)
    add("경보설비", "자동화재속보설비", building_type in ["의료시설", "노유자시설"], "노유자 및 의료시설 등에 설치.", "시행령 제13조", law_center_link)
    add("경보설비", "가스누설경보기", has_gas, "가스설비가 있는 경우 설치.", "시행령 제13조", law_center_link)

    # 피난구조설비
    add("피난구조설비", "피난기구(완강기, 구조대 등)", floors >= 4, "4층 이상 건물에서 피난기구 설치 필요.", "시행령 제17조", law_center_link)
    add("피난구조설비", "인명구조기구", building_type in ["숙박시설", "노유자시설"], "숙박 및 노유자시설 등에서 설치.", "시행령 제17조", law_center_link)
    add("피난구조설비", "유도등", (
        has_basement or building_type in ["숙박시설", "노유자시설", "공동주택"] or area >= 1000
    ), "모든 건물의 주요 피난경로에 설치.", "시행령 제17조", law_center_link)
    add("피난구조설비", "유도표지", (
        building_type in ["숙박시설", "노유자시설", "공동주택"] or has_basement
    ), "비상구 및 대피 경로 표시에 사용.", "시행령 제17조", law_center_link)
    add("피난구조설비", "피난유도선", (
        has_basement or sub_type in ["고시원", "영화관"]
    ), "지하공간 등에서 유도선 설치.", "시행령 제17조", law_center_link)
    add("피난구조설비", "비상조명등", has_basement, "정전 시 대피 조도를 위한 등기구 설치.", "시행령 제17조", law_center_link)
    add("피난구조설비", "휴대용비상조명등", building_type in ["숙박시설"], "숙박시설 객실 등에 비치.", "시행령 제17조", law_center_link)

    # 소화용수설비
    add("소화용수설비", "상수도소화용수설비", area >= 1000, "연면적 기준 이상 건물은 소화용 상수도 확보.", "시행령 제15조", law_center_link)
    add("소화용수설비", "소화수조 및 저수조", area >= 1000, "상수도 미공급 지역 또는 대형 시설에서 필요.", "시행령 제15조", law_center_link)

    # 소화활동설비
    add("소화활동설비", "제연설비", (
        basement_area >= 1000 or building_type == "지하상가"
    ), "지하공간 또는 대규모 시설에 설치.", "시행령 제15조", law_center_link)
    add("소화활동설비", "연결송수관설비", area >= 5000 and floors >= 5, "대형 고층건물에서 소방차 연결 필요.", "시행령 제15조", law_center_link)
    add("소화활동설비", "연결살수설비", area >= 5000, "대규모 건물에서 살수용 연결설비 설치.", "시행령 제15조", law_center_link)
    add("소화활동설비", "비상콘센트설비", area >= 1000 and floors >= 5, "화재 시 전력공급 확보용 콘센트.", "시행령 제15조", law_center_link)
    add("소화활동설비", "무선통신보조설비", floors >= 5, "고층건물에서 무선통신 가능성을 확보.", "시행령 제15조", law_center_link)

    # 기타설비
    add("기타설비", "방화문, 방화셔터", (
        floors >= 4 or area >= 1000
    ), "화재 확산 방지를 위한 방화구획 시설.", "시행령 제15조", law_center_link)
    add("기타설비", "비상구, 피난통로", True, "모든 건물에 확보되어야 할 피난 경로.", "시행령 제17조", law_center_link)
    add("기타설비", "방염", building_type in ["숙박시설", "노유자시설"], "내장재의 불연성 확보를 위한 처리.", "시행령 제15조", law_center_link)

    return categorized

# 결과 표시
st.title("소방시설 설치 기준 자동 조회")
st.write("입력한 건물 정보에 따라 필요한 소방시설 내역을 확인해보세요.")

results = get_fire_facilities(building_type, area, floors, has_basement, has_it_room, has_gas, occupancy, approval_date, sub_type, basement_area, layered_use, has_auto_suppression_alt)

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
                <b>관련 기준/법령:</b> <a href='{r['law_link']}' target='_blank'>{r['law_text']}</a>
              </div>
            </div>
            """, unsafe_allow_html=True)
