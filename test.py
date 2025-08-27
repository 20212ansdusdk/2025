import streamlit as st
import random
from dataclasses import dataclass

# --------------------------
# 데이터 정의
# --------------------------
ING_EMOJI = {
    "돼지고기": "🐷", "소고기": "🐮", "닭고기": "🐔", "새우": "🦐", "김치": "🥬",
    "부추": "🌿", "양파": "🧅", "마늘": "🧄", "버섯": "🍄", "두부": "🧊",
    "당면": "🍜", "고구마": "🍠", "옥수수": "🌽"
}
ALL_ING = list(ING_EMOJI.keys())

COOK_METHODS = ["찜", "군만두", "튀김"]
COOK_EMOJI = {"찜": "🥟", "군만두": "🍳", "튀김": "🍤"}

# --------------------------
# 데이터 구조
# --------------------------
@dataclass
class Order:
    required_protein: str
    must_have: list
    optional_mixes: list
    pleats_min: int
    pleats_max: int
    method: str
    time_target: tuple
    note: str

@dataclass
class Attempt:
    ingredients: list
    pleats: int
    method: str
    cook_time: float

# --------------------------
# 주문 생성
# --------------------------
def generate_order() -> Order:
    protein = random.choice(["돼지고기", "소고기", "닭고기", "새우"])
    must_have = random.sample([i for i in ALL_ING if i != protein], 2)
    optional_mixes = random.sample([i for i in ALL_ING if i not in must_have + [protein]], 2)
    pleats_min = random.randint(8, 12)
    pleats_max = pleats_min + random.randint(2, 5)
    method = random.choice(COOK_METHODS)
    time_target = (random.randint(7, 10), random.randint(11, 15))
    note = random.choice(["손님이 아삭한 식감을 원한다.", "담백한 맛을 원한다.", "풍미가 깊었으면 좋겠다."])
    return Order(protein, must_have, optional_mixes, pleats_min, pleats_max, method, time_target, note)

# --------------------------
# 점수 채점
# --------------------------
def evaluate(order: Order, attempt: Attempt) -> tuple[int, list]:
    score = 100
    reasons = []

    if order.required_protein not in attempt.ingredients:
        score -= 40
        reasons.append("메인 단백질이 빠졌습니다!")

    for m in order.must_have:
        if m not in attempt.ingredients:
            score -= 20
            reasons.append(f"필수 재료 {m}이(가) 빠졌습니다!")

    if not (order.pleats_min <= attempt.pleats <= order.pleats_max):
        score -= 15
        reasons.append("주름 수가 조건에 맞지 않습니다.")

    if order.method != attempt.method:
        score -= 15
        reasons.append("조리법이 다릅니다.")

    if not (order.time_target[0] <= attempt.cook_time <= order.time_target[1]):
        score -= 10
        reasons.append("조리 시간이 맞지 않습니다.")

    return max(score, 0), reasons

# --------------------------
# 사장님 츤데레 멘트
# --------------------------
def boss_comment(score: int) -> str:
    if score >= 90:
        return random.choice([
            "이 정도면 만두 장인이다! 가게 인수해라~",
            "만두 신 내렸냐? 내가 배워야겠다.",
            "이 맛… 고향만두 광고 들어오겠다!"
        ])
    elif score >= 70:
        return random.choice([
            "오~ 손님들 좋아하시겠다. 근데 주름 좀 삐뚤삐뚤하네?",
            "맛은 괜찮은데… 이게 만두냐, 송편이냐?",
            "흠… 합격! 하지만 아직 사장님 손맛은 멀었다~"
        ])
    elif score >= 50:
        return random.choice([
            "속이 너무 꽉 찼어, 이러다 터지겠다!",
            "만두는 만두인데… 이게 찐만두냐 군만두냐, 정체를 모르겠다?",
            "에이… 반은 성공, 반은 실패야."
        ])
    else:
        return random.choice([
            "이게 만두냐 송편이냐 당장 그만둬라!!!",
            "손님이 먹고 바로 도망가겠다!",
            "네가 싸온 도시락은 내가 안 먹는다…"
        ])

# --------------------------
# Streamlit 앱
# --------------------------
st.set_page_config(page_title="고향만두 만들기 게임", page_icon="🥟", layout="centered")

if "order" not in st.session_state:
    st.session_state.order = generate_order()
if "done" not in st.session_state:
    st.session_state.done = False

st.title("🥟 고향만두 만들기 게임")

# 주문 카드 (진행 중일 때만)
if not st.session_state.done and st.session_state.order:
    order = st.session_state.order
    st.subheader("📋 오늘의 주문")
    st.markdown(f"- 메인 단백질: {ING_EMOJI[order.required_protein]} {order.required_protein}")
    st.markdown(f"- 필수 재료: " + " ".join(f"{ING_EMOJI[i]} {i}" for i in order.must_have))
    st.markdown(f"- 선호 믹스: " + " ".join(f"{ING_EMOJI[i]} {i}" for i in order.optional_mixes))
    st.markdown(f"- 주름 수: {order.pleats_min} ~ {order.pleats_max}개")
    st.markdown(f"- 조리법: {COOK_EMOJI[order.method]} {order.method}")
    st.markdown(f"- 시간: {order.time_target[0]} ~ {order.time_target[1]}분")
    st.markdown(f"- 메모: {order.note}")

    # 만들기 입력
    st.subheader("🥢 만두 만들기")
    st.multiselect("속 재료를 고르세요", options=ALL_ING, key="ingredients")
    st.number_input("주름 수", min_value=0, max_value=30, step=1, key="pleats")
    st.radio("조리법", COOK_METHODS, key="method")
    st.slider("조리 시간 (분)", min_value=5, max_value=20, step=1, key="cook_time")

    if st.button("제출하기"):
        attempt = Attempt(
            st.session_state.ingredients,
            st.session_state.pleats,
            st.session_state.method,
            float(st.session_state.cook_time),
        )
        score, reasons = evaluate(st.session_state.order, attempt)
        st.session_state.result = (score, reasons)
        st.session_state.done = True
        st.rerun()

# 결과 화면
if st.session_state.done:
    score, reasons = st.session_state.result
    st.subheader("📊 라운드 결과")
    st.metric("획득 점수", score)
    for r in reasons:
        st.write("- " + r)
    st.markdown(f"### 👨‍🍳 사장님 한마디: {boss_comment(score)}")

    if st.button("다시 시작"):
        st.session_state.order = generate_order()
        st.session_state.done = False
        st.rerun()
