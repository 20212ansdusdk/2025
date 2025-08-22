import streamlit as st
import random

st.set_page_config(page_title="던전 탐험 게임", layout="centered")

st.title("🧙 던전 탐험 RPG")

# 세션 상태 초기화
if "hp" not in st.session_state:
    st.session_state.hp = 100
    st.session_state.gold = 0
    st.session_state.log = ["던전에 입장했습니다... ⚔️"]
    st.session_state.game_over = False

# 이벤트 함수
def explore():
    event = random.choice(["monster", "treasure", "trap", "nothing"])
    if event == "monster":
        dmg = random.randint(5, 30)
        st.session_state.hp -= dmg
        st.session_state.log.append(f"👹 몬스터를 만났습니다! 전투 중 {dmg} 피해를 입었습니다.")
    elif event == "treasure":
        gold = random.randint(10, 50)
        st.session_state.gold += gold
        st.session_state.log.append(f"💰 보물을 발견했습니다! {gold} 골드를 얻었습니다.")
    elif event == "trap":
        dmg = random.randint(10, 20)
        st.session_state.hp -= dmg
        st.session_state.log.append(f"☠️ 함정을 밟았습니다! {dmg} 피해를 입었습니다.")
    else:
        st.session_state.log.append("😶 아무 일도 일어나지 않았습니다...")

    if st.session_state.hp <= 0:
        st.session_state.log.append("💀 당신은 던전에서 쓰러졌습니다...")
        st.session_state.game_over = True

# 탐험 버튼
if not st.session_state.game_over:
    if st.button("탐험하기"):
        explore()

# 현재 상태
st.subheader("📊 현재 상태")
st.write(f"❤️ HP: {st.session_state.hp}")
st.write(f"🪙 GOLD: {st.session_state.gold}")

# 로그 출력
st.subheader("📜 탐험 기록")
for entry in st.session_state.log[::-1]:
    st.write(entry)

# 게임 오버시
if st.session_state.game_over:
    st.error("게임 오버! 😢")
    if st.button("다시 시작하기"):
        st.session_state.hp = 100
        st.session_state.gold = 0
        st.session_state.log = ["새로운 던전에 입장했습니다... ⚔️"]
        st.session_state.game_over = False
