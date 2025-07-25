import streamlit as st
import random


st.header("✊ ✋ ✌️ 가위바위보 게임")

choices = ["가위", "바위", "보"]
user_choice = st.radio("가위, 바위, 보 중 하나를 선택하세요:", choices, horizontal=True)

if st.button("결과 확인"):
    computer_choice = random.choice(choices)
    st.write(f"컴퓨터의 선택: {computer_choice}")

    if user_choice == computer_choice:
        st.info("비겼어요! 😐")
    elif (
        (user_choice == "가위" and computer_choice == "보") or
        (user_choice == "바위" and computer_choice == "가위") or
        (user_choice == "보" and computer_choice == "바위")
    ):
        st.success("이겼어요! 🎉")
    else:
        st.error("졌어요! 😢")