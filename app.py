import streamlit as st
import requests

st.set_page_config(page_title="🎭 심리테스트 + 영화 추천", page_icon="🎬", layout="wide")

st.title("🎭 심리테스트 앱 + 🎬 TMDB 영화 추천")
st.write("답변을 바탕으로 당신에게 어울리는 **장르**를 결정하고, TMDB에서 **인기 영화 5개**를 추천해드려요!")

# =========================
# 사이드바: TMDB API KEY 입력
# =========================
st.sidebar.header("🔑 TMDB 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password", placeholder="여기에 API Key 입력")

# =========================
# 장르 매핑
# =========================
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14
}

# =========================
# 질문(예시) - 기존 심리테스트에 맞게 수정 가능
# =========================
st.subheader("🧠 심리테스트 질문")

q1 = st.radio("1) 주말에 가장 하고 싶은 것은?", ["밖에서 활동", "집에서 푹 쉬기", "친구들과 수다", "혼자 몰입"])
q2 = st.radio("2) 영화에서 더 끌리는 요소는?", ["박진감", "웃음", "감동", "상상력", "설렘", "미래/기술"])
q3 = st.radio("3) 주인공 성격은 어떤 게 좋아?", ["강인함", "유쾌함", "진중함", "몽환적", "다정함", "천재/괴짜"])
q4 = st.radio("4) 스토리 분위기는?", ["빠르고 강렬", "가볍고 밝음", "현실적", "비현실적", "달달", "신비롭거나 실험적"])

# =========================
# 답변 분석 -> 장르 결정
# =========================
def decide_genre(a1, a2, a3, a4):
    score = {g: 0 for g in GENRES.keys()}

    # q1 반영
    if a1 == "밖에서 활동":
        score["액션"] += 2
        score["SF"] += 1
    elif a1 == "집에서 푹 쉬기":
        score["드라마"] += 2
        score["로맨스"] += 1
    elif a1 == "친구들과 수다":
        score["코미디"] += 2
        score["로맨스"] += 1
    elif a1 == "혼자 몰입":
        score["판타지"] += 2
        score["SF"] += 1
        score["드라마"] += 1

    # q2 반영(가장 중요)
    mapping_q2 = {
        "박진감": "액션",
        "웃음": "코미디",
        "감동": "드라마",
        "상상력": "판타지",
        "설렘": "로맨스",
        "미래/기술": "SF",
    }
    score[mapping_q2[a2]] += 4

    # q3 반영
    mapping_q3 = {
        "강인함": "액션",
        "유쾌함": "코미디",
        "진중함": "드라마",
        "몽환적": "판타지",
        "다정함": "로맨스",
        "천재/괴짜": "SF",
    }
    score[mapping_q3[a3]] += 2

    # q4 반영
    if a4 == "빠르고 강렬":
        score["액션"] += 2
    elif a4 == "가볍고 밝음":
        score["코미디"] += 2
    elif a4 == "현실적":
        score["드라마"] += 2
    elif a4 == "비현실적":
        score["판타지"] += 2
    elif a4 == "달달":
        score["로맨스"] += 2
    elif a4 == "신비롭거나 실험적":
        score["SF"] += 2
        score["판타지"] += 1

    # 최고 점수 장르 반환
    best_genre = max(score, key=score.get)
    return best_genre, score

# =========================
# TMDB 호출
# =========================
def fetch_movies_by_genre(api_key: str, genre_id: int, n: int = 5):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "page": 1
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    return results[:n]

def poster_url(poster_path: str):
    if not poster_path:
        return None
    return "https://image.tmdb.org/t/p/w500" + poster_path

def recommend_reason(genre: str, score_dict: dict):
    # 가장 크게 반영된 이유를 간단히 요약
    top = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)[:2]
    if genre == "액션":
        return "당신은 **박진감**과 **강렬한 전개**를 선호하는 편이라 액션이 잘 맞아요."
    if genre == "코미디":
        return "당신은 **가벼운 분위기**와 **웃음 포인트**가 있는 작품에서 힐링을 얻는 편이에요."
    if genre == "드라마":
        return "당신은 **현실적인 이야기**와 **감정선**이 깊은 작품에 몰입하는 편이에요."
    if genre == "SF":
        return "당신은 **미래/기술**이나 **실험적인 설정**에서 흥미를 느끼는 편이에요."
    if genre == "로맨스":
        return "당신은 **설렘**과 **관계의 변화**를 중심으로 한 이야기에 끌리는 편이에요."
    if genre == "판타지":
        return "당신은 **상상력**과 **비현실적 세계관**에서 재미를 느끼는 편이에요."
    return f"답변 분석 결과 **{genre}** 성향이 가장 높게 나왔어요. (상위 점수: {top})"

# =========================
# 결과 보기 버튼
# =========================
st.divider()
if st.button("✅ 결과 보기", use_container_width=True):
    if not api_key:
        st.error("사이드바에 TMDB API Key를 입력해 주세요!")
        st.stop()

    # 1) 장르 결정
    genre, score_dict = decide_genre(q1, q2, q3, q4)
    genre_id = GENRES[genre]

    st.success(f"🎯 당신에게 추천하는 장르: **{genre}** (ID: {genre_id})")
    st.info(recommend_reason(genre, score_dict))

    # 2) TMDB에서 영화 5개 가져오기
    try:
        movies = fetch_movies_by_genre(api_key, genre_id, n=5)
    except requests.RequestException as e:
        st.error(f"TMDB API 호출에 실패했어요: {e}")
        st.stop()

    if not movies:
        st.warning("해당 장르에서 영화를 가져오지 못했어요. 잠시 후 다시 시도해 주세요.")
        st.stop()

    st.subheader("🍿 추천 영화 5편")

    # 3) 영화 표시
    for m in movies:
        title = m.get("title") or m.get("name") or "제목 없음"
        rating = m.get("vote_average", 0)
        overview = m.get("overview") or "줄거리 정보가 없어요."
        purl = poster_url(m.get("poster_path"))

        with st.container(border=True):
            cols = st.columns([1, 2])
            with cols[0]:
                if purl:
                    st.image(purl, use_container_width=True)
                else:
                    st.write("🖼️ 포스터 없음")
            with cols[1]:
                st.markdown(f"### {title}")
                st.write(f"⭐ 평점: **{rating:.1f}**")
                st.write(overview)

                # 4) 추천 이유(간단)
                st.markdown("**이 영화를 추천하는 이유**")
                st.write(f"- 당신의 테스트 결과가 **{genre}** 성향으로 나와서, 이 장르의 **인기 작품**을 추천했어요.")

