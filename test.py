# app.py
# 고향만두 만들기 게임 (Streamlit)
# 실행: streamlit run app.py

import random
import time
from dataclasses import dataclass, asdict
import streamlit as st

st.set_page_config(page_title="고향만두 만들기", page_icon="🥟", layout="wide")

# ---------- 데이터 모델 ----------
ING_EMOJI = {
    "돼지고기": "🐖",
    "닭고기": "🐓",
    "새우": "🦐",
    "두부": "🧀",  # 대체 아이콘
    "부추": "🌿",
    "양파": "🧅",
    "마늘": "🧄",
    "김치": "🥬",
    "당면": "🍜",
    "표고": "🍄",
    "당근": "🥕",
}
COOK_EMOJI = {"찜": "🧺", "군만두": "🍳", "물만두": "🥘"}

ALL_ING = list(ING_EMOJI.keys())
PROTEINS = ["돼지고기", "닭고기", "새우", "두부"]
COOK_METHODS = ["찜", "군만두", "물만두"]

@dataclass
class Order:  # 손님 주문(요구사항)
    required_protein: str
    optional_mixes: list
    must_have: list         # 반드시 포함
    avoid: list             # 넣으면 감점
    pleats_min: int
    pleats_max: int
    method: str
    time_target: tuple      # (min, max) 분 단위
    note: str               # 특이사항/힌트

@dataclass
class Attempt:  # 플레이어 선택(결과 평가용)
    ingredients: list
    pleats: int
    method: str
    cook_time: float

# ---------- 유틸 ----------
def method_time_range(method: str, difficulty: str):
    # 난이도에 따라 허용 범위를 조금 타이트하게
    if method == "찜":
        base = (7, 10)
    elif method == "군만두":
        base = (6, 8)
    else:  # 물만두
        base = (4, 6)
    tighten = {"쉬움": 1.5, "보통": 1, "어려움": 0.5}[difficulty]
    span = (base[1] - base[0]) * tighten
    mid = sum(base)/2
    return (round(mid - span/2, 1), round(mid + span/2, 1))

def new_order(difficulty: str) -> Order:
    random.seed(time.time_ns())
    protein = random.choice(PROTEINS)
    method = random.choice(COOK_METHODS)

    # 필수/회피 재료 생성
    pool = [i for i in ALL_ING if i != protein]
    must_have = random.sample(pool, 2)
    avoid = random.sample([i for i in pool if i not in must_have], 1)

    # 선택(섞으면 가산점)
    optional_mixes = random.sample([i for i in pool if i not in must_have + avoid], 2)

    # 주름 조건
    if difficulty == "쉬움":
        pleats_min, pleats_max = 6, 8
    elif difficulty == "보통":
        pleats_min, pleats_max = 7, 10
    else:
        pleats_min, pleats_max = 8, 12

    tmin, tmax = method_time_range(method, difficulty)
    note = random.choice([
        "속은 촉촉하게, 겉은 바삭하게!",
        "향이 너무 강하면 안 좋아하세요.",
        "식감 조화 중요! 너무 질기면 감점!",
        "담백한 맛 선호.",
        "매콤한 풍미 좋아하심.",
    ])

    return Order(
        required_protein=protein,
        optional_mixes=optional_mixes,
        must_have=must_have,
        avoid=avoid,
        pleats_min=pleats_min,
        pleats_max=pleats_max,
        method=method,
        time_target=(tmin, tmax),
        note=note
    )

def score_attempt(order: Order, attempt: Attempt):
    points = 0
    reasons = []

    # 1) 단백질 정확도
    if order.required_protein in attempt.ingredients:
        points += 30
        reasons.append(f"✅ 메인 단백질 일치: {order.required_protein}")
    else:
        reasons.append(f"❌ 메인 단백질 누락 (요구: {order.required_protein})")

    # 2) 필수 재료
    must_hits = [i for i in order.must_have if i in attempt.ingredients]
    points += 10 * len(must_hits)
    if len(must_hits) == len(order.must_have):
        reasons.append(f"✅ 필수 재료 모두 포함: {', '.join(order.must_have)}")
    else:
        miss = [i for i in order.must_have if i not in attempt.ingredients]
        reasons.append(f"❌ 필수 재료 누락: {', '.join(miss)}")

    # 3) 회피 재료
    avoid_hits = [i for i in order.avoid if i in attempt.ingredients]
    points -= 15 * len(avoid_hits)
    if avoid_hits:
        reasons.append(f"⚠️ 회피 재료 포함: {', '.join(avoid_hits)}")

    # 4) 선택 믹스(가산점)
    mix_hits = [i for i in order.optional_mixes if i in attempt.ingredients]
    points += 5 * len(mix_hits)
    if mix_hits:
        reasons.append(f"✨ 취향 저격 믹스 추가: {', '.join(mix_hits)}")

    # 5) 주름 수
    if order.pleats_min <= attempt.pleats <= order.pleats_max:
        points += 20
        reasons.append(f"✅ 주름 수 적정 ({attempt.pleats}개)")
    else:
        # 범위 밖이면 오차당 감점
        diff = min(abs(attempt.pleats - order.pleats_min), abs(attempt.pleats - order.pleats_max))
        penalty = min(20, diff * 4)
        points -= penalty
        reasons.append(f"⚠️ 주름 수 범위({order.pleats_min}~{order.pleats_max}) 벗어남: {attempt.pleats}개 (−{penalty}점)")

    # 6) 조리법
    if attempt.method == order.method:
        points += 20
        reasons.append(f"✅ 조리법 일치: {attempt.method}")
    else:
        points -= 10
        reasons.append(f"❌ 조리법 불일치 (요구: {order.method})")

    # 7) 시간
    tmin, tmax = order.time_target
    if tmin <= attempt.cook_time <= tmax:
        points += 15
        reasons.append(f"✅ 조리 시간 적정 ({attempt.cook_time}분)")
    else:
        off = min(abs(attempt.cook_time - tmin), abs(attempt.cook_time - tmax))
        penalty = min(15, round(off * 5))
        points -= penalty
        reasons.append(f"⚠️ 시간 범위({tmin}~{tmax}분) 벗어남: {attempt.cook_time}분 (−{penalty}점)")

    # 보정
    points = max(0, min(100, points))
    return points, reasons

def pill(text):
    return f"<span style='padding:4px 10px;border-radius:999px;background:#f1f5f9;border:1px solid #e2e8f0;font-size:0.9rem;'>{text}</span>"

# ---------- 상태 초기화 ----------
if "started" not in st.session_state:
    st.session_state.started = False
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "보통"
if "order" not in st.session_state:
    st.session_state.order = None
if "round" not in st.session_state:
    st.session_state.round = 0
if "score_total" not in st.session_state:
    st.session_state.score_total = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "time_limit" not in st.session_state:
    st.session_state.time_limit = 60  # 초

# ---------- 사이드바 ----------
with st.sidebar:
    st.title("🥟 고향만두 만들기")
    st.caption("주문 조건에 맞춰 만두를 만들어 보세요!")

    st.session_state.difficulty = st.radio("난이도", ["쉬움", "보통", "어려움"], index=["쉬움","보통","어려움"].index(st.session_state.difficulty), horizontal=True)
    st.session_state.time_limit = st.slider("라운드 제한 시간(초)", 30, 120, st.session_state.time_limit, step=5)

    colA, colB = st.columns(2)
    if colA.button("게임 시작" if not st.session_state.started else "새 라운드"):
        st.session_state.started = True
        st.session_state.order = new_order(st.session_state.difficulty)
        st.session_state.round += 1
        st.session_state.start_time = time.monotonic()
        st.experimental_rerun()

    if colB.button("전체 초기화"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("점수")
    st.metric(label="총 점수", value=st.session_state.get("score_total", 0))
    st.metric(label="라운드", value=st.session_state.get("round", 0))

# ---------- 메인 UI ----------
st.header("만두 가게: 오늘의 주문을 맞춰라!")

if not st.session_state.started:
    st.info("왼쪽에서 **게임 시작**을 눌러 첫 주문을 받아보세요!")
    st.stop()

order: Order = st.session_state.order

# 남은 시간 표시
if st.session_state.start_time:
    elapsed = time.monotonic() - st.session_state.start_time
else:
    elapsed = 0.0
remain = max(0, st.session_state.time_limit - int(elapsed))
progress = remain / st.session_state.time_limit if st.session_state.time_limit else 0
st.progress(progress, text=f"남은 시간: {remain}초")

# 시간이 끝나면 자동 평가(재료 공백 시 0점 방지용 기본값)
if remain == 0:
    st.warning("⏰ 시간 종료! 현재 선택으로 평가합니다.")
    # 기본 입력값을 안전하게 읽기
    ingredients = st.session_state.get("ingredients", [])
    pleats = st.session_state.get("pleats", order.pleats_min)
    method = st.session_state.get("method", order.method)
    cook_time = st.session_state.get("cook_time", sum(order.time_target)/2)
    attempt = Attempt(ingredients, pleats, method, float(cook_time))
    pts, reasons = score_attempt(order, attempt)
    st.session_state.score_total += pts
    st.session_state.order = None
    st.session_state.start_time = None

    st.subheader("라운드 결과")
    st.metric("획득 점수", pts)
    for r in reasons:
        st.write(r)
    if st.button("다음 라운드"):
        st.session_state.order = new_order(st.session_state.difficulty)
        st.session_state.round += 1
        st.session_state.start_time = time.monotonic()
        st.experimental_rerun()
    st.stop()

# 주문 카드
with st.container(border=True):
    st.subheader("📋 오늘의 주문")
    c1, c2, c3 = st.columns([3,2,2])
    with c1:
        st.markdown(
            f"{pill('메인 단백질')} {ING_EMOJI[order.required_protein]} **{order.required_protein}**  "
        , unsafe_allow_html=True)
        st.markdown(
            f"{pill('필수 재료')} " + "  ".join(f"{ING_EMOJI[i]} {i}" for i in order.must_have),
            unsafe_allow_html=True
        )
        st.markdown(
            f"{pill('선호 믹스')} " + "  ".join(f"{ING_EMOJI[i]} {i}" for i in order.optional_mixes),
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(f"{pill('주름 수')} **{order.pleats_min} ~ {order.pleats_max}개**", unsafe_allow_html=True)
        st.markdown(f"{pill('조리법')} {COOK_EMOJI[order.method]} **{order.method}**", unsafe_allow_html=True)
        st.markdown(f"{pill('시간')} **{order.time_target[0]}~{order.time_target[1]}분**", unsafe_allow_html=True)
    with c3:
        st.markdown(f"{pill('사장님 메모')} _{order.note}_", unsafe_allow_html=True)

st.markdown("### 🧑‍🍳 나의 조합")

# 재료 선택
ingredients = st.multiselect(
    "속 재료를 고르세요 (메인 단백질 + 추가 재료)",
    options=ALL_ING,
    default=st.session_state.get("ingredients", []),
    format_func=lambda x: f"{ING_EMOJI[x]} {x}",
    help="필수/회피 재료 조건을 참고하세요!"
)
st.session_state.ingredients = ingredients

# 주름 + 조리법 + 시간
cA, cB, cC = st.columns(3)
with cA:
    pleats = st.number_input("주름(개)", min_value=4, max_value=16, value=st.session_state.get("pleats", order.pleats_min), step=1)
    st.session_state.pleats = int(pleats)
with cB:
    method = st.radio("조리법", COOK_METHODS, index=COOK_METHODS.index(st.session_state.get("method", order.method)), horizontal=True)
    st.session_state.method = method
with cC:
    cook_time = st.slider("조리 시간(분)", 2.0, 12.0, value=float(st.session_state.get("cook_time", sum(order.time_target)/2)), step=0.5)
    st.session_state.cook_time = cook_time

st.markdown("---")

# 제출 버튼
submit_col1, submit_col2 = st.columns([1,3])
with submit_col1:
    submit = st.button("만두 완성! ✅", type="primary")
with submit_col2:
    st.caption("버튼을 누르면 현재 선택으로 즉시 평가됩니다.")

if submit:
    attempt = Attempt(ingredients, int(pleats), method, float(cook_time))
    pts, reasons = score_attempt(order, attempt)
    st.session_state.score_total += pts

    st.subheader("라운드 결과")
    st.metric("획득 점수", pts)
    for r in reasons:
        st.write(r)

    st.session_state.order = None
    st.session_state.start_time = None

    if st.button("다음 라운드 ▶"):
        st.session_state.order = new_order(st.session_state.difficulty)
        st.session_state.round += 1
        st.session_state.start_time = time.monotonic()
        st.experimental_rerun()

# 힌트 섹션
with st.expander("🔎 팁/도움말 보기"):
    st.markdown(
        """
- **메인 단백질**은 반드시 포함해야 큰 점수를 받아요.  
- **필수 재료**는 놓치지 말고, **회피 재료**는 넣지 마세요.  
- **주름 수**는 범위를 벗어나면 감점돼요.  
- **조리법 + 시간**은 주문의 핵심 포인트! 범위를 맞추면 보너스가 커요.  
- 라운드 제한 시간 안에 제출하지 못하면, 현재 선택으로 자동 평가됩니다.
        """
    )
