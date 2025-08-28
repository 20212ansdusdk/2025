import streamlit as st
import random, time

# --------------------
# 게임 기본 데이터
# --------------------
ALL_ING = ["돼지고기", "소고기", "닭고기", "김치", "버섯", "두부", "부추", "양배추", "당면", "새우"]
COOK_METHODS = ["찜", "군만두", "튀김"]

class Order:
    def __init__(self, required_protein, extra_ings, pleat_range, cook_range):
        self.required_protein = required_protein
        self.extra_ings = extra_ings
        self.pleat_range = pleat_range
        self.cook_range = cook_range

class Attempt:
    def __init__(self, ingredients, pleats, method, cook_time):
        self.ingredients = ingredients
        self.pleats = pleats
        self.method = method
        self.cook_time = cook_time

# --------------------
# 난이도별 주문 생성
# --------------------
def generate_order(difficulty):
    protein = random.choice(["돼지고기", "소고기", "닭고기", "새우"])
    if difficulty == "Easy":
        extra_ings = random.sample(ALL_ING, 1)
        pleat_range = (8, 14)
        cook_range = (8, 15)
    elif difficulty == "Normal":
        extra_ings = random.sample(ALL_ING, 2)
        pleat_range = (10, 15)
        cook_range = (10, 14)
    else:  # Hard
        extra_ings = random.sample(ALL_ING, 3)
        pleat_range = (12, 14)
        cook_range = (11, 13)
    return Order(protein, extra_ings, pleat_range, cook_range)

# --------------------
# 난이도별 제한시간
# --------------------
def get_time_limit(difficulty):
    if difficulty == "Easy":
        return 40
    elif difficulty == "Normal":
        return 30
    else:
        return 20

# --------------------
# 평가 함수
# --------------------
def evaluate(order, attempt):
    score = 100
    reasons = []

    # 단백질 확인
    if order.required_protein not in attempt.ingredients:
        score -= 40
        reasons.append("메인 단백질이 빠졌습니다!")

    # 추가 재료 확인
    missing = [ing for ing in order.extra_ings if ing not in attempt.ingredients]
    if missing:
        score -= 20
        reasons.append(f"빠진 추가 재료: {', '.join(missing)}")

    # 주름 수 확인
    if not (order.pleat_range[0] <= attempt.pleats <= order.pleat_range[1]):
        score -= 20
        reasons.append(f"주름 수가 맞지 않습니다 (요구: {order.pleat_range[0]}~{order.pleat_range[1]}개)")

    # 조리 시간 확인
    if not (order.cook_range[0] <= attempt.cook_time <= order.cook_range[1]):
        score -= 20
        reasons.append(f"조리 시간이 맞지 않습니다 (요구: {order.cook_range[0]}~{order.cook_range[1]}분)")

    return max(score, 0), reasons

# --------------------
# 사장님 멘트
# --------------------
def boss_comment(score):
    if score >= 80:
        return "오~ 그래 이 정도면 만두지! 잘했어!"
    elif score >= 50:
        return "흠... 먹을 순 있겠군. 하지만 아직 멀었어!"
    elif score > 0:
        return "이게 만두냐 송편이냐? 당장 그만둬라!"
    else:
        return "🤦‍♂️ 아예 못 먹겠다. 장사 접어라!"

# --------------------
# 세션 상태 초기화
# --------------------
if "step" not in st.session_state:
    st.session_state.step = 0
if "difficulty" not in st.session_state:
    st.session_state.difficulty = None
if "order" not in st.session_state:
    st.session_state.order = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --------------------
# Step 0: 난이도 선택
# --------------------
if st.session_state.step == 0:
    st.title("🥟 고향만두 만들기 게임")
    st.subheader("난이도를 선택하세요")

    if st.button("Easy"):
        st.session_state.difficulty = "Easy"
        st.session_state.step = 1
        st.rerun()
    if st.button("Normal"):
        st.session_state.difficulty = "Normal"
        st.session_state.step = 1
        st.rerun()
    if st.button("Hard"):
        st.session_state.difficulty = "Hard"
        st.session_state.step = 1
        st.rerun()

# --------------------
# Step 1: 주문 확인
# --------------------
elif st.session_state.step == 1:
    if st.session_state.order is None:
        st.session_state.order = generate_order(st.session_state.difficulty)
    order = st.session_state.order

    st.subheader("📋 오늘의 주문")
    st.write(f"- 메인 단백질: {order.required_protein}")
    st.write(f"- 추가 재료: {', '.join(order.extra_ings)}")
    st.write(f"- 주름: {order.pleat_range[0]}~{order.pleat_range[1]}개")
    st.write(f"- 조리 시간: {order.cook_range[0]}~{order.cook_range[1]}분")

    if st.button("시작하기"):
        st.session_state.start_time = time.time()
        st.session_state.step = 2
        st.rerun()

# --------------------
# Step 2: 속재료 선택
# --------------------
elif st.session_state.step == 2:
    elapsed = int(time.time() - st.session_state.start_time)
    limit = get_time_limit(st.session_state.difficulty)

    st.progress(min(elapsed / limit, 1.0))
    if elapsed > limit:
        st.error("⏰ 제한시간 초과! 실패했습니다.")
        if st.button("다시 시작"):
            st.session_state.step = 0
            st.session_state.order = None
            st.rerun()
    else:
        st.multiselect("속 재료를 고르세요", ALL_ING, key="ingredients")
        if st.button("다음"):
            st.session_state.step = 3
            st.rerun()

# --------------------
# Step 3: 주름 / 조리법 / 시간
# --------------------
elif st.session_state.step == 3:
    elapsed = int(time.time() - st.session_state.start_time)
    limit = get_time_limit(st.session_state.difficulty)

    st.progress(min(elapsed / limit, 1.0))
    if elapsed > limit:
        st.error("⏰ 제한시간 초과! 실패했습니다.")
        if st.button("다시 시작"):
            st.session_state.step = 0
            st.session_state.order = None
            st.rerun()
    else:
        st.number_input("주름 수", 0, 30, key="pleats")
        st.radio("조리법", COOK_METHODS, key="method")
        st.slider("조리 시간 (분)", 5, 20, key="cook_time")
        if st.button("완성하기"):
            st.session_state.step = 4
            st.rerun()

# --------------------
# Step 4: 결과 + 평가
# --------------------
elif st.session_state.step == 4:
    score, reasons = evaluate(
        st.session_state.order,
        Attempt(
            st.session_state.ingredients,
            st.session_state.pleats,
            st.session_state.method,
            float(st.session_state.cook_time),
        )
    )

    st.subheader("📊 라운드 결과")
    st.metric("획득 점수", score)
    for r in reasons:
        st.write("- " + r)

    # 👨‍🍳 사장님 멘트 (크게 강조)
    st.markdown("## 👨‍🍳 사장님 한마디")
    st.markdown(
        f"<div style='font-size:45px; font-weight:bold; color:#d9534f; text-align:center; margin-top:30px;'>{boss_comment(score)}</div>",
        unsafe_allow_html=True
    )

    if st.button("다시 시작"):
        st.session_state.step = 0
        st.session_state.order = None
        st.rerun()
