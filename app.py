import streamlit as st
import requests

st.set_page_config(page_title="🎭 MBTI 심리테스트 + 🎬 TMDB 추천", page_icon="🎬", layout="wide")

# =========================
# Sidebar: TMDB API Key
# =========================
st.sidebar.header("🔑 TMDB 설정")
api_key = st.sidebar.text_input("TMDB API Key", type="password", placeholder="여기에 API Key 입력")

st.title("🎭 MBTI 기반 심리테스트 + 🎬 영화 추천")
st.caption("답변으로 MBTI를 추정하고, 성향에 맞는 장르를 골라 TMDB 인기 영화 5편을 추천해요.")

# =========================
# Genre IDs
# =========================
GENRES = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

# =========================
# TMDB functions
# =========================
def fetch_movies_by_genre(api_key: str, genre_id: int, n: int = 5):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "page": 1,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return (data.get("results") or [])[:n]

def poster_url(poster_path: str | None):
    if not poster_path:
        return None
    return "https://image.tmdb.org/t/p/w500" + poster_path

# =========================
# MBTI Test Questions (10)
# Each question contributes to one axis: EI / SN / TF / JP
# Option A gives +1 to first letter, option B gives +1 to second letter.
# =========================
QUESTIONS = [
    # E / I (3)
    {"axis": "EI", "q": "1) 모임이 끝난 뒤 에너지는?", "a": ("사람들과 있으면 더 충전된다", "E"), "b": ("혼자 있어야 회복된다", "I")},
    {"axis": "EI", "q": "2) 쉬는 날 계획이 없다면?", "a": ("누군가 만나서 나가고 싶다", "E"), "b": ("집에서 혼자 시간을 보내고 싶다", "I")},
    {"axis": "EI", "q": "3) 낯선 환경에서 나는?", "a": ("먼저 말을 걸며 분위기를 만든다", "E"), "b": ("조용히 관찰하며 적응한다", "I")},

    # S / N (3)
    {"axis": "SN", "q": "4) 이야기/영화에서 더 끌리는 건?", "a": ("현실감 있는 설정과 디테일", "S"), "b": ("상징/세계관/숨은 의미", "N")},
    {"axis": "SN", "q": "5) 문제를 풀 때 나는?", "a": ("검증된 방법과 경험을 따른다", "S"), "b": ("새로운 아이디어로 접근한다", "N")},
    {"axis": "SN", "q": "6) 대화할 때 선호는?", "a": ("구체적인 예시/사실 중심", "S"), "b": ("가능성/미래/아이디어 중심", "N")},

    # T / F (2)
    {"axis": "TF", "q": "7) 갈등 상황에서 더 우선은?", "a": ("논리적으로 맞는 판단", "T"), "b": ("상대의 감정과 관계", "F")},
    {"axis": "TF", "q": "8) 피드백을 줄 때 나는?", "a": ("솔직하게 핵심을 말한다", "T"), "b": ("상처받지 않게 완곡하게 말한다", "F")},

    # J / P (2)
    {"axis": "JP", "q": "9) 여행 스타일은?", "a": ("계획표대로 착착 진행", "J"), "b": ("그때그때 끌리는 대로", "P")},
    {"axis": "JP", "q": "10) 마감이 있을 때 나는?", "a": ("미리미리 끝내는 편", "J"), "b": ("막판 집중력이 잘 나온다", "P")},
]

# =========================
# UI: Collect Answers
# =========================
st.subheader("🧩 MBTI 질문 (총 10문항)")
answers = []

for item in QUESTIONS:
    choice = st.radio(
        item["q"],
        [item["a"][0], item["b"][0]],
        key=item["q"],
        horizontal=False,
    )
    # store the letter chosen
    letter = item["a"][1] if choice == item["a"][0] else item["b"][1]
    answers.append((item["axis"], letter))

# =========================
# MBTI scoring
# =========================
def compute_mbti(ans):
    score = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for axis, letter in ans:
        score[letter] += 1

    mbti = ""
    mbti += "E" if score["E"] >= score["I"] else "I"
    mbti += "S" if score["S"] >= score["N"] else "N"
    mbti += "T" if score["T"] >= score["F"] else "F"
    mbti += "J" if score["J"] >= score["P"] else "P"
    return mbti, score

# =========================
# MBTI -> Genre mapping with weighted logic
# This is transparent and tweakable.
# =========================
def mbti_to_genre(mbti: str, score: dict):
    genre_score = {g: 0 for g in GENRES.keys()}
    reasons = []

    # E/I influences
    if mbti[0] == "E":
        genre_score["코미디"] += 2
        genre_score["액션"] += 1
        reasons.append("E(외향) 성향 → 에너지/활동감 있는 **코미디·액션** 가산")
    else:
        genre_score["드라마"] += 2
        genre_score["판타지"] += 1
        reasons.append("I(내향) 성향 → 몰입/서사 중심 **드라마·판타지** 가산")

    # S/N influences
    if mbti[1] == "S":
        genre_score["액션"] += 1
        genre_score["드라마"] += 2
        reasons.append("S(감각) 성향 → 현실 디테일/현실감 **드라마·액션** 가산")
    else:
        genre_score["SF"] += 2
        genre_score["판타지"] += 2
        reasons.append("N(직관) 성향 → 세계관/상상력 **SF·판타지** 크게 가산")

    # T/F influences
    if mbti[2] == "T":
        genre_score["SF"] += 2
        genre_score["액션"] += 1
        reasons.append("T(사고) 성향 → 구조/아이디어/전개 **SF·액션** 가산")
    else:
        genre_score["로맨스"] += 2
        genre_score["드라마"] += 1
        reasons.append("F(감정) 성향 → 관계/감정선 **로맨스·드라마** 가산")

    # J/P influences
    if mbti[3] == "J":
        genre_score["드라마"] += 1
        genre_score["액션"] += 1
        reasons.append("J(판단) 성향 → 서사/목표 지향 전개 **드라마·액션** 가산")
    else:
        genre_score["코미디"] += 1
        genre_score["판타지"] += 1
        reasons.append("P(인식) 성향 → 자유로운 전개/변주 **코미디·판타지** 가산")

    # Tie-breaker: use raw axis scores (more confident axis boosts its related genres)
    # confidence = difference between two letters in each axis
    conf_EI = abs(score["E"] - score["I"])
    conf_SN = abs(score["S"] - score["N"])
    conf_TF = abs(score["T"] - score["F"])
    conf_JP = abs(score["J"] - score["P"])

    if mbti[1] == "N" and conf_SN >= 2:
        genre_score["SF"] += 1
        genre_score["판타지"] += 1
        reasons.append("N 성향이 뚜렷함 → **SF·판타지** 추가 가산")
    if mbti[2] == "F" and conf_TF >= 1:
        genre_score["로맨스"] += 1
        reasons.append("F 성향 반영 → **로맨스** 추가 가산")
    if mbti[0] == "E" and conf_EI >= 2:
        genre_score["코미디"] += 1
        reasons.append("E 성향이 뚜렷함 → **코미디** 추가 가산")

    best_genre = max(genre_score, key=genre_score.get)
    return best_genre, genre_score, reasons

# =========================
# Button: Show Result
# =========================
st.divider()

if st.button("✅ 결과 보기", use_container_width=True):
    if not api_key:
        st.error("사이드바에 TMDB API Key를 입력해 주세요!")
        st.stop()

    mbti, axis_score = compute_mbti(answers)
    genre, genre_score, reasons = mbti_to_genre(mbti, axis_score)
    genre_id = GENRES[genre]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🔎 테스트 결과")
        st.metric("추정 MBTI", mbti)
        st.write("**축 점수(답변 요약)**")
        st.write(f"- E: {axis_score['E']} / I: {axis_score['I']}")
        st.write(f"- S: {axis_score['S']} / N: {axis_score['N']}")
        st.write(f"- T: {axis_score['T']} / F: {axis_score['F']}")
        st.write(f"- J: {axis_score['J']} / P: {axis_score['P']}")

    with col2:
        st.subheader("🎯 추천 장르")
        st.success(f"당신에게 추천하는 장르: **{genre}** (ID: {genre_id})")
        st.markdown("**이 장르를 추천하는 이유(성향 기반)**")
        for r in reasons[:4]:
            st.write(f"- {r}")

    # Fetch movies
    try:
        movies = fetch_movies_by_genre(api_key, genre_id, n=5)
    except requests.RequestException as e:
        st.error(f"TMDB API 호출 실패: {e}")
        st.stop()

    if not movies:
        st.warning("해당 장르 영화 데이터를 가져오지 못했어요. 잠시 후 다시 시도해 주세요.")
        st.stop()

    st.subheader("🍿 추천 영화 5편")
    for m in movies:
        title = m.get("title") or "제목 없음"
        rating = float(m.get("vote_average") or 0)
        overview = m.get("overview") or "줄거리 정보가 없어요."
        purl = poster_url(m.get("poster_path"))

        # Simple per-movie reason (same basis but personalized text)
        per_movie_reason = (
            f"당신의 MBTI({mbti}) 성향을 바탕으로 **{genre}** 장르를 골랐고, "
            f"그 중에서도 TMDB에서 **인기 높은 작품**을 추천했어요."
        )

        with st.container(border=True):
            cols = st.columns([1, 2.2])
            with cols[0]:
                if purl:
                    st.image(purl, use_container_width=True)
                else:
                    st.write("🖼️ 포스터 없음")
            with cols[1]:
                st.markdown(f"### {title}")
                st.write(f"⭐ 평점: **{rating:.1f}**")
                st.write(overview)

                st.markdown("**이 영화를 추천하는 이유**")
                st.write(f"- {per_movie_reason}")

