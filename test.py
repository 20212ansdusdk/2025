import streamlit as st
import random, time

if "step" not in st.session_state:
    st.session_state.step = 0
if "difficulty" not in st.session_state:
    st.session_state.difficulty = None
if "order" not in st.session_state:
    st.session_state.order = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --------------------
# 난이도 선택
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
        # 난이도에 맞는 주문 생성
        st.session_state.order = generate_order(st.session_state.difficulty)
    order = st.session_state.order
    
    st.subheader("📋 오늘의 주문")
    st.write(order)
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
    st.progress(elapsed / limit)
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
    st.progress(elapsed / limit)
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
    score, reasons = evaluate(st.session_state.order, Attempt(
        st.session_state.ingredients,
        st.session_state.pleats,
        st.session_state.method,
        float(st.session_state.cook_time),
    ))
    st.subheader("📊 라운드 결과")
    st.metric("획득 점수", score)
    for r in reasons:
        st.write("- " + r)
    st.write("👨‍🍳 사장님 한마디:", boss_comment(score))

    if st.button("다시 시작"):
        st.session_state.step = 0
        st.session_state.order = None
        st.rerun()
