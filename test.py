import streamlit as st
import random

st.set_page_config(page_title="가위바위보 게임", layout="centered")

st.title("✊✋✌️ 가위바위보 게임")

# 선택지
choices = ["가위", "바위", "보"]

# 사용자 입력
user_choice = st.radio("당신의 선택은?", choices)

if st.button("결과 보기"):
    computer_choice = random.choice(choices)
    st.write(f"🤖 컴퓨터의 선택: **{computer_choice}**")
    st.write(f"🙂 당신의 선택: **{user_choice}**")

    # 승패 판정
    if user_choice == computer_choice:
        st.success("비겼습니다! 😅")
    elif (
        (user_choice == "가위" and computer_choice == "보")
        or (user_choice == "바위" and computer_choice == "가위")
        or (user_choice == "보" and computer_choice == "바위")
    ):
        st.balloons()
        st.success("이겼습니다! 🎉")
    else:
        st.error("졌습니다... 😢")
