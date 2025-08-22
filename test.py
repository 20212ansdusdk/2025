import streamlit as st

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
