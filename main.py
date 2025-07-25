import streamlit as st

st.title("👋 Streamlit 예제 앱")

# 입력 받기
name = st.text_input("이름을 입력하세요:")

# 버튼 클릭 시 인사 출력
if st.button("인사하기"):
    if name:
        st.success(f"안녕하세요, {name}님! Streamlit에 오신 걸 환영합니다 😊")
    else:
        st.warning("이름을 먼저 입력해주세요.")
