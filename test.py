# app.py
# 고향만두 만들기 게임 (Streamlit, 최신 버전 호환)
# 실행: streamlit run app.py

import random
import time
from dataclasses import dataclass
import streamlit as st

st.set_page_config(page_title="고향만두 만들기", page_icon="🥟", layout="wide")

# ---- 호환 유틸 (버전별 안전 가드) ---------------------------------
# rerun: st.rerun 우선, 없으면 experimental_rerun 사용
_RERUN_FN = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
def safe_rerun():
    if _RERUN_FN:
        _RERUN_FN()

def safe_container_with_border():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()

def safe_progress(value, text=None):
    """value: 0.0 ~ 1.0"""
    try:
        return st.progress(value, text=text)
    except TypeError:
        # 구버전은 0~100 정수만 허용
        pct = max(0, min(100, int(round(value * 100))))
        return st.progress(pct)

def safe_button(label, **kwargs):
    # 구버전에서 type="primary" 미지원 시 fallback
    try:
        return st.button(label, **kwargs)
    except TypeError:
        return st.button(label)

def safe_radio(label, options, **kwargs):
    try:
        return st.radio(label, options, **kwargs)
    except TypeError:
        # horizontal 미지원 대비
        kwargs.pop("horizontal", None)
        return st.radio(label, options, **kwargs)

# ---- 데이터 -------------------------------------------------------
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
class Order:
    required_protein: str
    optional_mixes: list
    must_have: list
    avoid: list
    pleats_min: int
    pleats_max: int
    method: str
    time_target: tuple  # (min, max)
    note: str

@dataclass
class Attempt:
    ingredients: list
    pleats: int
    method: str
    cook_time: float

# ---- 로직 --------------------------------------------------------
def method_time_range(method: str, difficulty: str):
    if method == "찜":
        base = (7, 10)
    elif method == "군만두":
        base = (6, 8)
    else:
        base = (4, 6)
    tighten = {"쉬움": 1.5, "보통": 1, "어려움": 0.5}[difficulty]
    span = (base[1] - base[0]) * tighten
    mid = (base[0] + base[1]) / 2
    return (round(mid - span / 2, 1), round(mid + span / 2, 1))

def new_order(difficulty: str) -> Order:
    random.seed(time.time_ns())
    protein = random.choice(PROTEINS)
    method = random.choice(COOK_METHODS)

    pool = [i for i in ALL_ING if i != protein]
    must_have = random.sample(pool, 2)
    avoid = random.sample([i for i in pool if i not in must_have], 1)
    optional_mixes = random.sample([i for i in pool if i not in must_have + avoid], 2)

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
        note=note,
    )

def score_attempt(order: Order, attempt: Attempt):
    points = 0
    reasons = []

    # 메인 단백질
    if order.required_protein in attempt.ingredients:
        points += 30
        reasons.append(f"✅ 메인 단백질 일치: {order.required_protein}")
    else:
        reasons.append(f"❌ 메인 단백질 누락 (요구: {order.required_protein})")

    # 필수 재료
    must_hits = [i for i in order.must_have if i in attempt.ingredients]
    points += 10 * len(must_hits)
    if len(must_hits) == len(order.must_have):
        reasons.append(f"✅ 필수 재료 모두 포함: {', '.join(order.must_have)}")
    else:
        miss = [i for i in order.must_have if i not in attempt.ingredients]
        reasons.append(f"❌ 필수 재료 누락: {', '.join(miss)}")

    # 회피 재료
    avoid_hits = [i for i in order.avoid if i in attempt.ingredients]
    points -= 15 * len(avoid_hits)
    if avoid_hits:
        reasons.append(f"⚠️ 회피 재료 포함: {', '.join(avoid_hits)}")

    # 선택 믹스(가산점)
    mix_hits = [i for i in order.optional_mixes if i in attempt.ingredients]
    points += 5 * len(mix_hits)
    if mix_hits:
        reasons.append(f"✨ 취향 저격 믹스 추가: {', '.join(mix_hits)}")

    # 주름 수
    if order.pleats_min <= attempt.pleats <= order.pleats_max:
        points += 20
        reasons.append(f"✅ 주름 수 적정 ({attempt.pleats}개)")
    else:
        diff = min(abs(attempt.pleats - order.pleats_min), abs(attempt.pleats - order.pleats_max))
        penalty = min(20, diff * 4)
        points -= penalty
        reasons.append(
            f"⚠️ 주름 수 범위({order.pleats_min}~{order.pleats_max}) 벗어남: {attempt.pleats}개 (−{penalty}점)"
        )

    # 조리법
    if attempt.method == order.method:
        points += 20
        reasons.append(f"✅ 조리법 일치: {attempt.method}")
    else:
        points -= 10
        reasons.append(f"❌ 조리법 불일치 (요구: {order.method})")

    # 시간
    tmin, tmax = order.time_target
    if tmin <= attempt.cook_time <= tmax:
        points += 15
        reasons.append(f"✅ 조리 시간 적정 ({attempt.cook_time}분)")
    else:
        off = min(abs(attempt.cook_time - tmin), abs(attempt.cook_time - tmax))
        penalty = min(15, round(off * 5))
        points -= penalty
        reasons.append(f"⚠️ 시간 범위({tmin}~{tmax}분) 벗어남: {attempt.cook_time}분 (−{penalty}점)")

    return max(0, min(100, points)), reasons

def pill(text):
    return f"<span style='padding:4px 10px;border-radius:999px;background:#f1f5f9;border:1px solid #e2e8f0;font-size:0.9rem;'>{text}</span>"

# ---- 상태 초기화 -----------------------------------------------
ss = st.session_state
ss.setdefault("started", False)
ss.setdefault("difficulty", "보통")
ss.setdefault("order", None)
ss.setdefault("round", 0)
ss.setdefault("score_total", 0)
ss.setdefault("start_time", None)
ss.setdefault("time_limit", 60)

# ---- 사이드바 ---------------------------------------------------
with st.sidebar:
    st.title("🥟 고향만두 만들기")
    st.caption("주문 조건에 맞춰 만두를 만들어 보세요!")

    ss.difficulty = safe_radio(
        "난이도", ["쉬움", "보통", "어려움"],
        index=["쉬움", "보통", "어려움"].index(ss.difficulty),
        horizontal=True
    )
    ss.time_limit = st.slider("라운드 제한 시간(초)", 30, 120, ss.time_limit, step=5)

    colA, colB = st.columns(2)
    if colA.button("게임 시작" if not ss.started else "새 라운드"):
        ss.started = True
        ss.order = new_order(ss.difficulty)
        ss.round += 1
        ss.start_time = time.monotonic()
        safe_rerun()

    if colB.button("전체 초기화"):
        keys = list(ss.keys())
        for k in keys:
            del ss[k]
        safe_rerun()

    st.markdown("---")
    st.subheader("점수")
    st.metric(label="총 점수", value=ss.get("score_total", 0))
    st.metric(label="라운드", value=ss.get("round", 0))

# ---- 메인 -------------------------------------------------------
st.header("만두 가게: 오늘의 주문을 맞춰라!")

if not ss.started:
    st.info("왼쪽에서 **게임 시작**을 눌러 첫 주문을 받아보세요!")
    st.stop()

order: Order = ss.order

# 남은 시간 계산 & 표시
elapsed = (time.monotonic() - ss.start_time) if ss.start_time else 0.0
remain = max(0, ss.time_limit - int(elapsed))
progress = (remain / ss.time_limit) if ss.time_limit else 0.0
safe_progress(progress, text=f"남은 시간: {remain}초")

# 시간 종료 시 자동 평가
if remain == 0:
    st.warning("⏰ 시간 종료! 현재 선택으로 평가합니다.")
    ingredients = ss.get("ingredients", [])
    pleats = int(ss.get("pleats", order.pleats_min))
    method = ss.get("method", order.method)
    cook_time = float(ss.get("cook_time", sum(order.time_target) / 2))
    attempt = Attempt(ingredients, pleats, method, cook_time)
    pts, reasons = score_attempt(order, attempt)
    ss.score_total += pts
    ss.order = None
    ss.start_time = None

    st.subheader("라운드 결과")
    st.metric("획득 점수", pts)
    for r in reasons:
        st.write(r)

    if st.button("다음 라운드 ▶"):
        ss.order = new_order(ss.difficulty)
        ss.round += 1
        ss.start_time = time.monotonic()
        safe_rerun()
    st.stop()

# 주문 카드
with safe_container_with_border():
    st.subheader("📋 오늘의 주문")
    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        st.markdown(f"{pill('메인 단백질')} {ING_EMOJI[order.required_protein]} **{order.required_protein}**", unsafe_allow_html=True)
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
ss.ingredients = st.multiselect(
    "속 재료를 고르세요 (메인 단백질 + 추가 재료)",
    options=ALL_ING,
    default=ss.get("ingredients", []),
    format_func=lambda x: f"{ING_EMOJI[x]} {x}",
    help="필수/회피 재료 조건을 참고하세요!"
)

# 주름/조리법/시간
cA, cB, cC = st.columns(3)
with cA:
    ss.pleats = int(st.number_input("주름(개)", min_value=4, max_value=16, value=int(ss.get("pleats", order.pleats_min)), step=1))
with cB:
    ss.method = safe_radio("조리법", COOK_METHODS, index=COOK_METHODS.index(ss.get("method", order.method)), horizontal=True)
with cC:
    ss.cook_time = st.slider("조리 시간(분)", 2.0, 12.0, value=float(ss.get("cook_time", sum(order.time_target)/2)), step=0.5)

st.markdown("---")

# 제출
submit = safe_button("만두 완성! ✅", type="primary")
st.caption("버튼을 누르면 현재 선택으로 즉시 평가됩니다.")

if submit:
    attempt = Attempt(ss.ingredients, ss.pleats, ss.method, float(ss.cook_time))
    pts, reasons = score_attempt(order, attempt)
    ss.score_total += pts

    st.subheader("라운드 결과")
    st.metric("획득 점수", pts)
    for r in reasons:
        st.write(r)

    ss.order = None
    ss.start_time = None

    if st.button("다음 라운드 ▶"):
        ss.order = new_order(ss.difficulty)
        ss.round += 1
        ss.start_time = time.monotonic()
        safe_rerun()

# 팁
with st.expander("🔎 팁/도움말 보기"):
    st.markdown(
        """
- **메인 단백질**은 반드시 포함해야 큰 점수를 받아요.  
- **필수 재료**는 놓치지 말고, **회피 재료**는 넣지 마세요.  
- **주름 수**는 범위를 벗어나면 감점돼요.  
- **조리법 + 시간**은 주문의 핵심 포인트! 범위를 맞추면 보너스가 커요.  
- 제한 시간 안에 제출하지 못하면, 현재 선택으로 자동 평가됩니다.
        """
    )
