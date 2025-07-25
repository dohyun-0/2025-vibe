import streamlit as st
import pandas as pd
import plotly.express as px

# 📥 데이터 로딩
@st.cache_data
def load_data():
    df_total = pd.read_csv("202506_202506_연령별인구현황_월간_합계.csv", encoding="cp949")
    return df_total

# 🧹 전처리 함수
def preprocess(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")].copy()
    
    # 시/도 컬럼 추가
    df["시도"] = df["행정구역"].apply(lambda x: x.split()[0])

    # 총인구수, 연령구간인구수 숫자형 변환
    df["총인구수"] = df["2025년06월_계_총인구수"].astype(str).str.replace(",", "").astype(int)
    df["연령구간인구수"] = df["2025년06월_계_연령구간인구수"].astype(str).str.replace(",", "").astype(int)

    # 연령 관련 열 추출
    age_cols = [col for col in df.columns if "세" in col and "계" in col]

    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)

    return df, age_cols

# 🚀 Streamlit 앱 시작
def main():
    st.set_page_config(page_title="인구 통계 시각화", layout="wide")
    st.title("📊 2025년 6월 연령별 인구 통계")

    df_raw = load_data()
    df, age_columns = preprocess(df_raw)

    tab1, tab2 = st.tabs(["🗺️ 시도별 총/연령구간 인구", "📈 행정구역별 연령 분포"])

    with tab1:
        st.subheader("시도별 총인구수 및 연령구간인구수")
        df_city = df.groupby("시도")[["총인구수", "연령구간인구수"]].sum().reset_index()
        option = st.radio("표시할 항목", ["총인구수", "연령구간인구수"], horizontal=True)
        fig = px.bar(df_city, x="시도", y=option, title=f"{option} (시도별)", text_auto=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("행정구역별 연령별 인구 분포")
        selected_region = st.selectbox("행정구역 선택", df["행정구역"].unique())
        row = df[df["행정구역"] == selected_region].iloc[0]
        df_age = pd.DataFrame({
            "연령": [col.split("_")[-1] for col in age_columns],
            "인구수": [row[col] for col in age_columns]
        })

        fig2 = px.line(df_age, x="연령", y="인구수", markers=True,
                       title=f"{selected_region} 연령별 인구 분포", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
