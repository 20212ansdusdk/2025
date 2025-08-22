# 쉽고 유명한 넌센스 퀴즈 (Streamlit)
import streamlit as st
import random
import re

st.set_page_config(page_title="쉽고 유명한 넌센스 퀴즈", layout="centered")
st.title("🧠 쉽고 유명한 넌센스 퀴즈")

# ✅ 쉬운/유명 문제 + 힌트 2단계, 정답 여러 표현 허용
QUIZZES = [
    {"q": "잠자는 소는?", "answers": ["잠수함", "잠수 한", "잠수한소", "잠수 한 소"],
     "hints": ["단어를 쪼개봐: '잠수' + '소'", "배 종류 떠올리기(OO함)"]},
    {"q": "세상에서 가장 억울한 도형은?", "answers": ["원통", "원통형", "원통해"],
     "hints": ["발음 장난: '원통해…'", "도형 이름 자체가 정답!"]},
    {"q": "사과가 웃으면?", "answers": ["풋사과", "풋 사과"],
     "hints": ["웃음소리: '풋!'", "덜 익은 사과를 뭐라 해?"]},
    {"q": "바나나가 웃으면?", "answers": ["바나나킥", "바나나 킥"],
     "hints": ["과자 이름 떠올리기", "축구 기술 이름과 같아!"]},
    {"q": "세상에서 가장 뜨거운 과일은?", "answers": ["열매"],
     "hints": ["온도 느낌 단어 포함", "'열' + 과일의 통칭"]},
    {"q": "오리가 얼면?", "answers": ["언덕"],
     "hints": ["오리=duck (영어 장난)", "얼면 '언' + duck = ?"]},
    {"q": "세상에서 가장 큰 콩은?", "answers": ["킹콩", "kingkong"],
     "hints": ["사람도 타는(?) 콩", "헐리우드 스타 몬스터"]},
    {"q": "사람들이 가장 많이 타는 차는?", "answers": ["기차"],
     "hints": ["대중교통", "레일 위 달려!"]},
    {"q": "세상에서 가장 무거운 새는?", "answers": ["앵무새"],
     "hints": ["단어 자체에 힌트", "'무'가 들어간다"]},
]

# --- 유틸: 입력 정규화 (공백/기호 제거, 소문자화) ---
def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9a-z가-힣]", "", s)
    return s

# --- 세션 상태 초기화 ---
if "order" not in st.session_state:
    st.session_state.order = list(range(len(QUIZZES)))
    random.shuffle(st.session_state.order)
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.hints_shown = 0
    st.session_state.revealed = False
    st.session_state.finished = False
    st.session_state.attempted = False  # 제출 시도 여부

idx = st.session_state.order[st.session_state.i]
quiz = QUIZZES[idx]

st.subheader(f"문제 {st.session_state.i + 1} / {len(QUIZZES)}")
st.write(quiz["q"])

# 입력
user = st.text_input(
    "정답을 입력하세요 (모르면 힌트를 눌러보세요!)",
    key=f"ans_{st.session_state.i}"
)

# 버튼들
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("제출", type="primary", use_container_width=True):
        if not st.session_state.revealed and not st.session_state.finished:
            st.session_state.attempted = True
            user_n = normalize(user)
            answers_n = [normalize(a) for a in quiz["answers"]]
            if user_n and user_n in answers_n:
                st.success("정답! 🎉")
                st.balloons()
                st.session_state.score += 1
                st.session_state.revealed = True
            else:
                st.error("앗, 오답… 😢 힌트를 눌러보세요!")

with col2:
    if st.button("힌트", use_container_width=True):
        if not st.session_state.revealed and st.session_state.hints_shown < 2:
            st.session_state.hints_shown += 1

with col3:
    if st.button("포기(정답보기)", use_container_width=True):
        st.info(f"정답: **{quiz['answers'][0]}**")
        st.session_state.revealed = True

with col4:
    next_label = "다음 문제" if st.session_state.i < len(QUIZZES) - 1 else "결과 보기"
    if st.button(next_label, use_container_width=True):
        # 최소한 한 번 시도하거나(제출/힌트/포기) 정답 공개 후에만 넘어가도록
        if st.session_state.revealed or st.session_state.hints_shown > 0 or st.session_state.attempted:
            if st.session_state.i < len(QUIZZES) - 1:
                st.session_state.i += 1
                st.session_state.hints_shown = 0
                st.session_state.revealed = False
                st.session_state.attempted = False
            else:
                st.session_state.finished = True
        else:
            st.warning("힌트 보거나 한 번 제출해본 뒤에 넘어가요!")

# 힌트 표시
if not st.session_state.revealed and st.session_state.hints_shown > 0:
    for k in range(st.session_state.hints_shown):
        st.info(f"힌트 {k+1}: {quiz['hints'][k]}")

# 진행 현황
st.write("---")
st.write(f"현재 점수: **{st.session_state.score}** / {len(QUIZZES)}")

# 결과 화면
if st.session_state.finished:
    st.success(f"퀴즈 완료! 최종 점수: {st.session_state.score} / {len(QUIZZES)}")
    if st.button("다시 시작"):
        st.session_state.order = list(range(len(QUIZZES)))
        random.shuffle(st.session_state.order)
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.hints_shown = 0
        st.session_state.revealed = False
        st.session_state.finished = False
        st.session_state.attempted = False
        # Streamlit 버전 호환: rerun 우선, 없으면 experimental_rerun
        try:
            st.rerun()
        except Exception:
            try:
                st.experimental_rerun()
            except Exception:
                pass# 쉽고 유명한 넌센스 퀴즈 (Streamlit)
import streamlit as st
import random
import re

st.set_page_config(page_title="쉽고 유명한 넌센스 퀴즈", layout="centered")
st.title("🧠 쉽고 유명한 넌센스 퀴즈")

# ✅ 쉬운/유명 문제 + 힌트 2단계, 정답 여러 표현 허용
QUIZZES = [
    {"q": "잠자는 소는?", "answers": ["잠수함", "잠수 한", "잠수한소", "잠수 한 소"],
     "hints": ["단어를 쪼개봐: '잠수' + '소'", "배 종류 떠올리기(OO함)"]},
    {"q": "세상에서 가장 억울한 도형은?", "answers": ["원통", "원통형", "원통해"],
     "hints": ["발음 장난: '원통해…'", "도형 이름 자체가 정답!"]},
    {"q": "사과가 웃으면?", "answers": ["풋사과", "풋 사과"],
     "hints": ["웃음소리: '풋!'", "덜 익은 사과를 뭐라 해?"]},
    {"q": "바나나가 웃으면?", "answers": ["바나나킥", "바나나 킥"],
     "hints": ["과자 이름 떠올리기", "축구 기술 이름과 같아!"]},
    {"q": "세상에서 가장 뜨거운 과일은?", "answers": ["열매"],
     "hints": ["온도 느낌 단어 포함", "'열' + 과일의 통칭"]},
    {"q": "오리가 얼면?", "answers": ["언덕"],
     "hints": ["오리=duck (영어 장난)", "얼면 '언' + duck = ?"]},
    {"q": "세상에서 가장 큰 콩은?", "answers": ["킹콩", "kingkong"],
     "hints": ["사람도 타는(?) 콩", "헐리우드 스타 몬스터"]},
    {"q": "사람들이 가장 많이 타는 차는?", "answers": ["기차"],
     "hints": ["대중교통", "레일 위 달려!"]},
    {"q": "세상에서 가장 무거운 새는?", "answers": ["앵무새"],
     "hints": ["단어 자체에 힌트", "'무'가 들어간다"]},
]

# --- 유틸: 입력 정규화 (공백/기호 제거, 소문자화) ---
def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9a-z가-힣]", "", s)
    return s

# --- 세션 상태 초기화 ---
if "order" not in st.session_state:
    st.session_state.order = list(range(len(QUIZZES)))
    random.shuffle(st.session_state.order)
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.hints_shown = 0
    st.session_state.revealed = False
    st.session_state.finished = False
    st.session_state.attempted = False  # 제출 시도 여부

idx = st.session_state.order[st.session_state.i]
quiz = QUIZZES[idx]

st.subheader(f"문제 {st.session_state.i + 1} / {len(QUIZZES)}")
st.write(quiz["q"])

# 입력
user = st.text_input(
    "정답을 입력하세요 (모르면 힌트를 눌러보세요!)",
    key=f"ans_{st.session_state.i}"
)

# 버튼들
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("제출", type="primary", use_container_width=True):
        if not st.session_state.revealed and not st.session_state.finished:
            st.session_state.attempted = True
            user_n = normalize(user)
            answers_n = [normalize(a) for a in quiz["answers"]]
            if user_n and user_n in answers_n:
                st.success("정답! 🎉")
                st.balloons()
                st.session_state.score += 1
                st.session_state.revealed = True
            else:
                st.error("앗, 오답… 😢 힌트를 눌러보세요!")

with col2:
    if st.button("힌트", use_container_width=True):
        if not st.session_state.revealed and st.session_state.hints_shown < 2:
            st.session_state.hints_shown += 1

with col3:
    if st.button("포기(정답보기)", use_container_width=True):
        st.info(f"정답: **{quiz['answers'][0]}**")
        st.session_state.revealed = True

with col4:
    next_label = "다음 문제" if st.session_state.i < len(QUIZZES) - 1 else "결과 보기"
    if st.button(next_label, use_container_width=True):
        # 최소한 한 번 시도하거나(제출/힌트/포기) 정답 공개 후에만 넘어가도록
        if st.session_state.revealed or st.session_state.hints_shown > 0 or st.session_state.attempted:
            if st.session_state.i < len(QUIZZES) - 1:
                st.session_state.i += 1
                st.session_state.hints_shown = 0
                st.session_state.revealed = False
                st.session_state.attempted = False
            else:
                st.session_state.finished = True
        else:
            st.warning("힌트 보거나 한 번 제출해본 뒤에 넘어가요!")

# 힌트 표시
if not st.session_state.revealed and st.session_state.hints_shown > 0:
    for k in range(st.session_state.hints_shown):
        st.info(f"힌트 {k+1}: {quiz['hints'][k]}")

# 진행 현황
st.write("---")
st.write(f"현재 점수: **{st.session_state.score}** / {len(QUIZZES)}")

# 결과 화면
if st.session_state.finished:
    st.success(f"퀴즈 완료! 최종 점수: {st.session_state.score} / {len(QUIZZES)}")
    if st.button("다시 시작"):
        st.session_state.order = list(range(len(QUIZZES)))
        random.shuffle(st.session_state.order)
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.hints_shown = 0
        st.session_state.revealed = False
        st.session_state.finished = False
        st.session_state.attempted = False
        # Streamlit 버전 호환: rerun 우선, 없으면 experimental_rerun
        try:
            st.rerun()
        except Exception:
            try:
                st.experimental_rerun()
            except Exception:
                passimport streamlit as st
import random
import re

st.set_page_config(page_title="쉽고 유명한 넌센스 퀴즈", layout="centered")
st.title("🧠 쉽고 유명한 넌센스 퀴즈")

# ✅ 넌센스 문제들 (정답 여러 형태 허용 + 힌트 2단계)
QUIZZES = [
    {
        "q": "잠자는 소는?",
        "answers": ["잠수함", "잠수 한", "잠수 한 소", "잠수함소"],
        "hints": ["단어를 쪼개봐: '잠수' + '소'", "배 종류를 떠올려봐…"]
    },
    {
        "q": "세상에서 가장 억울한 도형은?",
        "answers": ["원통", "원통형", "원통해"],
        "hints": ["발음 장난: '원통해…'", "도형 이름 자체가 정답!"]
    },
    {
        "q": "사과가 웃으면?",
        "answers": ["풋사과", "풋 사과"],
        "hints": ["웃음소리: '풋!'", "덜 익은 사과를 뭐라고 할까?"]
    },
    {
        "q": "바나나가 웃으면?",
        "answers": ["바나나킥", "바나나 킥"],
        "hints": ["과자 이름 떠올리기", "축구 기술 이름과 같아!"]
    },
    {
        "q": "세상에서 가장 뜨거운 과일은?",
        "answers": ["열매"],
        "hints": ["온도 관련 단어가 들어가", "'열' + 과일의 통칭"]
    },
    {
        "q": "오리가 얼면?",
        "answers": ["언덕"],
        "hints": ["영어 장난: 오리=duck", "얼면 '언' + duck = ?"]
    },
    {
        "q": "세상에서 가장 큰 콩은?",
        "answers": ["킹콩", "kingkong"],
        "hints": ["사람도 타는(?) 콩", "헐리우드에 자주 나오는 그 친구"]
    },
    {
        "q": "사람들이 가장 많이 타는 차는?",
        "answers": ["기차"],
        "hints": ["대중교통", "레일 위를 달려!"]
    },
    {
        "q": "세상에서 가장 무거운 새는?",
        "answers": ["앵무새"],
        "hints": ["단어 자체에 힌트가 있어", "'무'가 들어간다"]
    },
]

# --- 유틸: 입력 정규화 (공백/기호 제거, 소문자화) ---
def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9a-z가-힣]", "", s)
    return s

# --- 세션 상태 초기화 ---
if "order" not in st.session_state:
    st.session_state.order = list(range(len(QUIZZES)))
    random.shuffle(st.session_state.order)
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.hints_shown = 0
    st.session_state.revealed = False
    st.session_state.finished = False

idx = st.session_state.order[st.session_state.i]
quiz = QUIZZES[idx]

st.subheader(f"문제 {st.session_state.i + 1} / {len(QUIZZES)}")
st.write(quiz["q"])

# 입력
user = st.text_input("정답을 입력하세요 (모르면 힌트를 눌러봐요!)", key=f"ans_{st.session_state.i}")

col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    if st.button("제출", type="primary", use_container_width=True):
        if not st.session_state.revealed and not st.session_state.finished:
            user_n = normalize(user)
            answers_n = [normalize(a) for a in quiz["answers"]]
            if user_n and user_n in answers_n:
                st.success("정답! 🎉")
                st.balloons()
                st.session_state.score += 1
                st.session_state.revealed = True
            else:
                st.error("앗, 오답… 😢 힌트를 눌러보세요!")

with col2:
    if st.button("힌트", use_container_width=True):
        if not st.session_state.revealed and st.session_state.hints_shown < 2:
            st.session_state.hints_shown += 1

with col3:
    if st.button("포기(정답보기)", use_container_width=True):
        st.info(f"정답: **{quiz['answers'][0]}**")
        st.session_state.revealed = True

with col4:
    next_label = "다음 문제" if st.session_state.i < len(QUIZZES) - 1 else "결과 보기"
    if st.button(next_label, use_container_width=True):
        if st.session_state.i < len(QUIZZES) - 1:
            st.session_state.i += 1
            st.session_state.hints_shown = 0
            st.session_state.revealed = False
        else:
            st.session_state.finished = True

# 힌트 표시
if not st.session_state.revealed and st.session_state.hints_shown > 0:
    for k in range(st.session_state.hints_shown):
        st.info(f"힌트 {k+1}: {quiz['hints'][k]}")

# 진행 현황
st.write("---")
st.write(f"현재 점수: **{st.session_state.score}** / {len(QUIZZES)}")

# 결과 화면
if st.session_state.finished:
    st.success(f"퀴즈 완료! 최종 점수: {st.session_state.score} / {len(QUIZZES)}")
    if st.button("다시 시작"):
        st.session_state.order = list(range(len(QUIZZES)))
        random.shuffle(st.session_state.order)
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.hints_shown = 0
        st.session_state.revealed = False
        st.session_state.finished = False
        st.experimental_rerun()import streamlit as st
import random
import re

st.set_page_config(page_title="쉽고 유명한 넌센스 퀴즈", layout="centered")
st.title("🧠 쉽고 유명한 넌센스 퀴즈")

# ✅ 넌센스 문제들 (정답 여러 형태 허용 + 힌트 2단계)
QUIZZES = [
    {
        "q": "잠자는 소는?",
        "answers": ["잠수함", "잠수 한", "잠수 한 소", "잠수함소"],
        "hints": ["단어를 쪼개봐: '잠수' + '소'", "배 종류를 떠올려봐…"]
    },
    {
        "q": "세상에서 가장 억울한 도형은?",
        "answers": ["원통", "원통형", "원통해"],
        "hints": ["발음 장난: '원통해…'", "도형 이름 자체가 정답!"]
    },
    {
        "q": "사과가 웃으면?",
        "answers": ["풋사과", "풋 사과"],
        "hints": ["웃음소리: '풋!'", "덜 익은 사과를 뭐라고 할까?"]
    },
    {
        "q": "바나나가 웃으면?",
        "answers": ["바나나킥", "바나나 킥"],
        "hints": ["과자 이름 떠올리기", "축구 기술 이름과 같아!"]
    },
    {
        "q": "세상에서 가장 뜨거운 과일은?",
        "answers": ["열매"],
        "hints": ["온도 관련 단어가 들어가", "'열' + 과일의 통칭"]
    },
    {
        "q": "오리가 얼면?",
        "answers": ["언덕"],
        "hints": ["영어 장난: 오리=duck", "얼면 '언' + duck = ?"]
    },
    {
        "q": "세상에서 가장 큰 콩은?",
        "answers": ["킹콩", "kingkong"],
        "hints": ["사람도 타는(?) 콩", "헐리우드에 자주 나오는 그 친구"]
    },
    {
        "q": "사람들이 가장 많이 타는 차는?",
        "answers": ["기차"],
        "hints": ["대중교통", "레일 위를 달려!"]
    },
    {
        "q": "세상에서 가장 무거운 새는?",
        "answers": ["앵무새"],
        "hints": ["단어 자체에 힌트가 있어", "'무'가 들어간다"]
    },
]

# --- 유틸: 입력 정규화 (공백/기호 제거, 소문자화) ---
def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[^0-9a-z가-힣]", "", s)
    return s

# --- 세션 상태 초기화 ---
if "order" not in st.session_state:
    st.session_state.order = list(range(len(QUIZZES)))
    random.shuffle(st.session_state.order)
    st.session_state.i = 0
    st.session_state.score = 0
    st.session_state.hints_shown = 0
    st.session_state.revealed = False
    st.session_state.finished = False

idx = st.session_state.order[st.session_state.i]
quiz = QUIZZES[idx]

st.subheader(f"문제 {st.session_state.i + 1} / {len(QUIZZES)}")
st.write(quiz["q"])

# 입력
user = st.text_input("정답을 입력하세요 (모르면 힌트를 눌러봐요!)", key=f"ans_{st.session_state.i}")

col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    if st.button("제출", type="primary", use_container_width=True):
        if not st.session_state.revealed and not st.session_state.finished:
            user_n = normalize(user)
            answers_n = [normalize(a) for a in quiz["answers"]]
            if user_n and user_n in answers_n:
                st.success("정답! 🎉")
                st.balloons()
                st.session_state.score += 1
                st.session_state.revealed = True
            else:
                st.error("앗, 오답… 😢 힌트를 눌러보세요!")

with col2:
    if st.button("힌트", use_container_width=True):
        if not st.session_state.revealed and st.session_state.hints_shown < 2:
            st.session_state.hints_shown += 1

with col3:
    if st.button("포기(정답보기)", use_container_width=True):
        st.info(f"정답: **{quiz['answers'][0]}**")
        st.session_state.revealed = True

with col4:
    next_label = "다음 문제" if st.session_state.i < len(QUIZZES) - 1 else "결과 보기"
    if st.button(next_label, use_container_width=True):
        if st.session_state.i < len(QUIZZES) - 1:
            st.session_state.i += 1
            st.session_state.hints_shown = 0
            st.session_state.revealed = False
        else:
            st.session_state.finished = True

# 힌트 표시
if not st.session_state.revealed and st.session_state.hints_shown > 0:
    for k in range(st.session_state.hints_shown):
        st.info(f"힌트 {k+1}: {quiz['hints'][k]}")

# 진행 현황
st.write("---")
st.write(f"현재 점수: **{st.session_state.score}** / {len(QUIZZES)}")

# 결과 화면
if st.session_state.finished:
    st.success(f"퀴즈 완료! 최종 점수: {st.session_state.score} / {len(QUIZZES)}")
    if st.button("다시 시작"):
        st.session_state.order = list(range(len(QUIZZES)))
        random.shuffle(st.session_state.order)
        st.session_state.i = 0
        st.session_state.score = 0
        st.session_state.hints_shown = 0
        st.session_state.revealed = False
        st.session_state.finished = False
        st.experimental_rerun()import streamlit as st

st.set_page_config(page_title="넌센스 퀴즈 게임", layout="centered")

st.title("🧠 넌센스 퀴즈 게임")

# 퀴즈 데이터 (문제, 정답, 힌트)
quiz_list = [
    {"q": "세상에서 가장 빠른 닭은?", "a": "후다닭", "hint": "허겁지겁 도망칠 때 나는 소리"},
    {"q": "자동차가 울면?", "a": "카센터", "hint": "차가 눈물이 나면 어디로 갈까요?"},
    {"q": "물고기가 다니는 학원은?", "a": "스쿨", "hint": "영어 단어 생각해봐~"},
    {"q": "세상에서 가장 센 벌은?", "a": "건벌", "hint": "이거 맞으면 집 무너짐"},
    {"q": "컴퓨터가 싫어하는 술은?", "a": "에러", "hint": "버그랑 비슷한 느낌"}
]

# 세션 초기화
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.show_hint = False
    st.session_state.solved = False

current = quiz_list[st.session_state.index]

st.subheader(f"문제 {st.session_state.index + 1} / {len(quiz_list)}")
st.write(current["q"])

# 사용자 입력
answer = st.text_input("정답을 입력하세요")

# 정답 확인
if st.button("제출"):
    if answer.strip() == current["a"]:
        st.success("정답입니다! 🎉")
        st.session_state.score += 1
        st.session_state.solved = True
    else:
        st.error("틀렸습니다... 😢")
        st.session_state.show_hint = True

# 힌트 표시
if st.session_state.show_hint and not st.session_state.solved:
    st.info(f"힌트: {current['hint']}")

# 다음 문제 버튼
if st.session_state.solved or st.session_state.show_hint:
    if st.button("다음 문제"):
        if st.session_state.index < len(quiz_list) - 1:
            st.session_state.index += 1
            st.session_state.show_hint = False
            st.session_state.solved = False
        else:
            st.balloons()
            st.success(f"퀴즈 종료! 최종 점수: {st.session_state.score}/{len(quiz_list)}")
