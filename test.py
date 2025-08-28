# app.py
# 실행: streamlit run app.py
import time
import random
from dataclasses import dataclass
import streamlit as st

# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="고향만두 만들기: 스텝 모드", page_icon="🥟", layout="centered")

# 버전 호환 유틸
_RERUN = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
def safe_rerun():
    if _RERUN:
        _RERUN()

def safe_progress(v, text=None):
    # v: 0.0~1.0
    try:
        st.progress(v, text=text)
    except TypeError:
        st.progress(int(max(0, min(100, round(v*100)))))

def pill(text):
    return f"<span style='padding:4px 10px;border-radius:999px;background:#f1f5f9;border:1px solid #e2e8f0;font-size:0.9rem;'>{text}</span>"

# ----------------- 게임 데이터 -----------------
ING_EMOJI = {
    "돼지고기": "🐖","닭고기": "🐓","새우": "🦐","두부": "🧊",
    "김치": "🥬","부추": "🌿","양파": "🧅","마늘": "🧄",
    "표고": "🍄","당근": "🥕","당면": "🍜"
}
ALL_ING = list(ING_EMOJI.keys())
PROTEINS = ["돼지고기","닭고기","새우","두부"]
COOK_METHODS = ["찜","군만두","물만두"]
COOK_EMOJI = {"찜":"🧺","군만두":"🍳","물만두":"🥘"}

@dataclass
class Order:
    required_protein: str
    must_have: list
    optional_mixes: list
    avoid: list
    pleats_min: int
    pleats_max: int
    method: str
    time_target: tuple  # (min,max) minutes
    note: str

@dataclass
class Attempt:
    ingredients: list
    pleats: int
    method: str
    cook_time: float

# ----------------- 난이도/타이머/주문 -----------------
def get_time_limit(difficulty: str) -> int:
    # 엄청 짧게: 쉬움 30초, 보통 20초, 어려움 12초
    return {"쉬움": 30, "보통": 20, "어려움": 12}[difficulty]

def method_time_range(method: str, difficulty: str):
    # 기본 범위(분)
    base = {"찜": (7,10), "군만두": (6,8), "물만두": (4,6)}[method]
    tighten = {"쉬움": 1.5, "보통": 1.0, "어려움": 0.5}[difficulty]
    span = (base[1]-base[0]) * tighten
    mid = (base[0]+base[1])/2
    return (round(mid - span/2, 1), round(mid + span/2, 1))

def generate_order(difficulty: str) -> Order:
    random.seed(time.time_ns())
    protein = random.choice(PROTEINS)
    method = random.choice(COOK_METHODS)

    pool = [i for i in ALL_ING if i != protein]
    # 난이도별 필수/회피/선호 개수
    must_n = {"쉬움":1, "보통":2, "어려움":3}[difficulty]
    must_have = random.sample(pool, must_n)
    avoid = random.sample([i for i in pool if i not in must_have], 1)
    optional_mixes = random.sample([i for i in pool if i not in must_have + avoid], 2)

    # 주름 범위(난이도 높을수록 빡빡)
    pleat_ranges = {"쉬움": (6,10), "보통": (8,12), "어려움": (10,12)}
    pleats_min, pleats_max = pleat_ranges[difficulty]

    tmin, tmax = method_time_range(method, difficulty)
    note = random.choice([
        "향이 너무 강하면 싫대요.",
        "담백하지만 감칠맛 있게!",
        "식감 중요! 질기면 감점.",
        "겉바속촉 선호.",
        "약간 매콤 OK."
    ])

    return Order(
        required_protein=protein,
        must_have=must_have,
        optional_mixes=optional_mixes,
        avoid=avoid,
        pleats_min=pleats_min,
        pleats_max=pleats_max,
        method=method,
        time_target=(tmin, tmax),
        note=note
    )

# ----------------- 채점 & 보스 멘트 -----------------
def score_attempt(order: Order, a: Attempt):
    points = 0
    reasons = []

    # 메인 단백질
    if order.required_protein in a.ingredients:
        points += 30; reasons.append(f"✅ 메인 단백질 일치: {order.required_protein}")
    else:
        reasons.append(f"❌ 메인 단백질 누락 (요구: {order.required_protein})")

    # 필수 재료
    must_hits = [i for i in order.must_have if i in a.ingredients]
    points += 10 * len(must_hits)
    if len(must_hits) == len(order.must_have):
        reasons.append(f"✅ 필수 재료 OK: {', '.join(order.must_have)}")
    else:
        miss = [i for i in order.must_have if i not in a.ingredients]
        reasons.append(f"❌ 필수 재료 누락: {', '.join(miss)}")

    # 회피 재료
    avoid_hits = [i for i in order.avoid if i in a.ingredients]
    if avoid_hits:
        points -= 15 * len(avoid_hits)
        reasons.append(f"⚠️ 회피 재료 포함: {', '.join(avoid_hits)}")

    # 선호 믹스 가산점
    mix_hits = [i for i in order.optional_mixes if i in a.ingredients]
    points += 5 * len(mix_hits)
    if mix_hits:
        reasons.append(f"✨ 취향 저격 믹스: {', '.join(mix_hits)}")

    # 주름
    if order.pleats_min <= a.pleats <= order.pleats_max:
        points += 20; reasons.append(f"✅ 주름 수 적정 ({a.pleats}개)")
    else:
        diff = min(abs(a.pleats - order.pleats_min), abs(a.pleats - order.pleats_max))
        penalty = min(20, diff*4)
        points -= penalty
        reasons.append(f"⚠️ 주름 범위({order.pleats_min}~{order.pleats_max}) 벗어남: {a.pleats}개 (−{penalty}점)")

    # 조리법
    if a.method == order.method:
        points += 20; reasons.append(f"✅ 조리법 일치: {a.method}")
    else:
        points -= 10; reasons.append(f"❌ 조리법 불일치 (요구: {order.method})")

    # 시간
    tmin, tmax = order.time_target
    if tmin <= a.cook_time <= tmax:
        points += 15; reasons.append(f"✅ 조리 시간 적정 ({a.cook_time}분)")
    else:
        off = min(abs(a.cook_time - tmin), abs(a.cook_time - tmax))
        penalty = min(15, round(off*5))
        points -= penalty
        reasons.append(f"⚠️ 시간 범위({tmin}~{tmax}분) 벗어남: {a.cook_time}분 (−{penalty}점)")

    return max(0, min(100, points)), reasons

def boss_comment(score: int) -> str:
    if score >= 90:
        lines = [
            "이 정도면 만두 장인이다! 가게 인수해라~",
            "만두 신 내렸냐? 내가 배워야겠다.",
            "이 맛… 고향만두 광고 들어오겠다!"
        ]
    elif score >= 70:
        lines = [
            "오~ 손님들 좋아하시겠다. 근데 주름 좀 삐뚤다?",
            "맛은 괜찮은데… 이게 만두냐, 송편이냐?",
            "합격! 하지만 아직 사장님 손맛은 멀었다~"
        ]
    elif score >= 50:
        lines = [
            "속이 너무 꽉 찼어, 이러다 터진다!",
            "만두는 만두인데… 정체가 애매하다?",
            "반은 성공, 반은 실패야."
        ]
    else:
        lines = [
            "이게 만두냐 송편이냐 당장 그만둬라!!!",
            "손님이 먹고 바로 도망가겠다!",
            "오늘은… 네 도시락 내가 안 먹는다…"
        ]
    return random.choice(lines)

# ----------------- 상태 초기화 -----------------
ss = st.session_state
ss.setdefault("step", 0)            # 0:난이도, 1:주문확인, 2:재료선택, 3:주름/조리, 4:결과
ss.setdefault("difficulty", "보통")
ss.setdefault("order", None)
ss.setdefault("start_time", None)
ss.setdefault("ingredients", [])
ss.setdefault("pleats", 8)
ss.setdefault("method", COOK_METHODS[0])
ss.setdefault("cook_time", 6.0)
ss.setdefault("result", None)       # (score, reasons, timed_out:bool)

# ----------------- 공통: 타이머 처리 -----------------
def time_left_secs() -> int:
    if not ss.start_time: return get_time_limit(ss.difficulty)
    limit = get_time_limit(ss.difficulty)
    elapsed = int(time.monotonic() - ss.start_time)
    return max(0, limit - elapsed)

def guard_timeout_and_autosubmit(current_step: int):
    """Step2, Step3에서 시간 초과 시 자동 채점 후 결과로 이동"""
    if current_step not in (2,3): return
    remain = time_left_secs()
    safe_progress((remain / get_time_limit(ss.difficulty)) if get_time_limit(ss.difficulty) else 0,
                  text=f"남은 시간: {remain}초")
    if remain == 0:
        # 현재 입력값으로 자동 채점
        order = ss.order
        attempt = Attempt(
            ingredients=ss.get("ingredients", []),
            pleats=int(ss.get("pleats", order.pleats_min)),
            method=ss.get("method", order.method),
            cook_time=float(ss.get("cook_time", (order.time_target[0]+order.time_target[1])/2)),
        )
        score, reasons = score_attempt(order, attempt)
        reasons = ["⏰ 제한시간 초과! 자동 제출되었습니다."] + reasons
        ss.result = (score, reasons, True)
        ss.step = 4
        safe_rerun()

# ----------------- UI 흐름 -----------------
st.title("🥟 고향만두 만들기 - 스텝 모드")

# Step 0: 난이도 선택
if ss.step == 0:
    st.subheader("난이도를 선택하세요")
    cols = st.columns(3)
    if cols[0].button("쉬움 (30초)"):
        ss.difficulty = "쉬움"; ss.order=None; ss.step=1; safe_rerun()
    if cols[1].button("보통 (20초)"):
        ss.difficulty = "보통"; ss.order=None; ss.step=1; safe_rerun()
    if cols[2].button("어려움 (12초)"):
        ss.difficulty = "어려움"; ss.order=None; ss.step=1; safe_rerun()

# Step 1: 주문 확인
elif ss.step == 1:
    if ss.order is None:
        ss.order = generate_order(ss.difficulty)
    order: Order = ss.order

    st.subheader("📋 오늘의 주문")
    st.markdown(f"{pill('메인 단백질')} {ING_EMOJI[order.required_protein]} **{order.required_protein}**", unsafe_allow_html=True)
    st.markdown(f"{pill('필수 재료')} " + "  ".join(f"{ING_EMOJI[i]} {i}" for i in order.must_have), unsafe_allow_html=True)
    st.markdown(f"{pill('선호 믹스')} " + "  ".join(f"{ING_EMOJI[i]} {i}" for i in order.optional_mixes), unsafe_allow_html=True)
    st.markdown(f"{pill('회피 재료')} " + "  ".join(f"{ING_EMOJI[i]} {i}" for i in order.avoid), unsafe_allow_html=True)
    st.markdown(f"{pill('주름 수')} **{order.pleats_min} ~ {order.pleats_max}개**", unsafe_allow_html=True)
    st.markdown(f"{pill('조리법')} {COOK_EMOJI[order.method]} **{order.method}**", unsafe_allow_html=True)
    st.markdown(f"{pill('시간')} **{order.time_target[0]}~{order.time_target[1]}분**", unsafe_allow_html=True)
    st.caption(f"사장님 메모: _{order.note}_")

    if st.button("시작하기 ▶"):
        # 입력 초기화 & 타이머 시작
        ss.ingredients = []
        ss.pleats = order.pleats_min
        ss.method = order.method
        ss.cook_time = round((order.time_target[0]+order.time_target[1])/2, 1)
        ss.start_time = time.monotonic()
        ss.step = 2
        safe_rerun()

# Step 2: 속재료 선택
elif ss.step == 2:
    guard_timeout_and_autosubmit(2)
    st.subheader("🥢 Step 2. 속 재료를 고르세요")
    st.multiselect(
        "메인 단백질 + 추가 재료를 선택",
        options=ALL_ING,
        key="ingredients",
        format_func=lambda x: f"{ING_EMOJI[x]} {x}",
        help="필수/회피/선호 조건을 참고하세요."
    )
    cols = st.columns(2)
    if cols[0].button("◀ 주문 다시 보기"):
        ss.step = 1; safe_rerun()
    if cols[1].button("다음 ▶"):
        ss.step = 3; safe_rerun()

# Step 3: 주름/조리법/시간
elif ss.step == 3:
    guard_timeout_and_autosubmit(3)
    order: Order = ss.order
    st.subheader("🔥 Step 3. 모양/조리 세팅")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.number_input("주름 수", min_value=4, max_value=16, step=1, key="pleats")
        st.caption(f"권장: {order.pleats_min}~{order.pleats_max}개")
    with c2:
        st.radio("조리법", COOK_METHODS, key="method", horizontal=True)
        st.caption(f"요구: {order.method}")
    with c3:
        st.slider("조리 시간(분)", min_value=2.0, max_value=12.0, step=0.5, key="cook_time")
        st.caption(f"목표: {order.time_target[0]}~{order.time_target[1]}분")

    cols = st.columns(2)
    if cols[0].button("◀ 이전"):
        ss.step = 2; safe_rerun()
    if cols[1].button("만두 완성! ✅"):
        attempt = Attempt(ss.ingredients, int(ss.pleats), ss.method, float(ss.cook_time))
        score, reasons = score_attempt(ss.order, attempt)
        ss.result = (score, reasons, False)
        ss.step = 4
        safe_rerun()

# Step 4: 결과
elif ss.step == 4:
    st.subheader("📊 결과")
    if ss.result is None:
        st.info("결과가 없습니다. 처음으로 돌아갑니다.")
        ss.step = 0; safe_rerun()

    score, reasons, timed_out = ss.result
    st.metric("획득 점수", score)
    if timed_out:
        st.warning("⏰ 제한시간 초과")

    for r in reasons:
        st.write("• " + r)

    st.markdown(f"### 👨‍🍳 사장님 한마디")
    st.write(boss_comment(score))

    cols = st.columns(2)
    if cols[0].button("같은 난이도로 다시 하기"):
        ss.order = None
        ss.result = None
        ss.start_time = None
        ss.step = 1
        safe_rerun()
    if cols[1].button("난이도 다시 선택"):
        ss.order = None
        ss.result = None
        ss.start_time = None
        ss.step = 0
        safe_rerun()
