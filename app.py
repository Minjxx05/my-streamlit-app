import streamlit as st

st.set_page_config(page_title="✨ 나를 소개합니다", page_icon="✨")

st.title("✨ 나를 소개합니다")

# 입력 UI
name = st.text_input("이름을 입력하세요")
major = st.text_input("학과를 입력하세요")

mbti_list = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]
mbti = st.selectbox("MBTI를 선택하세요", mbti_list)

interests = st.multiselect(
    "관심 분야를 선택하세요 (복수 선택 가능)",
    ["AI", "웹개발", "데이터분석", "게임", "디자인"]
)

# ✅ 기분 상태 선택 UI 추가
mood = st.selectbox(
    "오늘의 기분 상태를 선택하세요",
    ["아주 좋아요 😄", "좋아요 🙂", "그냥 그래요 😐", "피곤해요 😴", "우울해요 😢", "스트레스 받아요 😖"]
)

# 버튼
if st.button("소개 생성"):
    if not name or not major:
        st.warning("이름과 학과는 꼭 입력해 주세요!")
    else:
        interests_text = ", ".join(interests) if interests else "아직 탐색 중이에요"
        intro = (
            f"안녕하세요! 저는 **{major}**에 재학 중인 **{name}**입니다. "
            f"MBTI는 **{mbti}**이고, 관심 분야는 **{interests_text}**예요. "
            f"오늘은 기분이 **{mood}** 😊 앞으로 잘 부탁드려요!"
        )
        st.success("소개가 생성되었습니다!")
        st.write(intro)
