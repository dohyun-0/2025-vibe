import streamlit as st
import pandas as pd
import plotly.express as px

# 📥 데이터 로딩
@st.cache_data
def load_data():
    df_total = pd.read_csv("202506_202506_연령별인구현황_월간_합계.csv", encoding="cp949")
    df_gender = pd.read_csv("202506_202506_연령별인구현황_월간_남녀구분.csv", encoding="cp949")
    return df_total, df_gender

# 🧹 전처리 함수
def preprocess(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")].copy()
    df["시도"] = df["행정구역"].apply(lambda x: x.split()[0])
    df["총인구수"] = df["2025년06월_계_총인구수"].astype(str).str.replace(",", "").astype(int)
    df["연령구간인구수"] = df["2025년06월_계_연령구간인구수"].astype(str).str.replace(",", "").astype(int)
    age_cols = [col for col in df.columns if "세" in col and "계" in col]
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)
    return df, age_cols

def preprocess_gender(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")].copy()
    df["시도"] = df["행정구역"].apply(lambda x: x.split()[0])

    # 불필요한 열 제거
    drop_cols = [col for col in df.columns if "총인구수" in col or "연령구간인구수" in col]
    df = df.drop(columns=drop_cols)

    # 남녀 연령 관련 열만 선택
    male_cols = [col for col in df.columns if "_남_" in col and "세" in col]
    female_cols = [col for col in df.columns if "_여_" in col and "세" in col]

    for col in male_cols + female_cols:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)

    return df, male_cols, female_cols

# 🚀 Streamlit 앱
def main():
    st.set_page_config(page_title="인구 통계 시각화", layout="wide")
    st.title("📊 2025년 6월 연령별 인구 통계")

    df_total, df_gender = load_data()
    df_total, age_cols = preprocess(df_total)
    df_gender, male_cols, female_cols = preprocess_gender(df_gender)

    tab1, tab2, tab3 = st.tabs(["🗺️ 시도별 총/연령구간 인구", "📈 연령별 인구 분포", "👥 남녀 인구 분포"])

    # 📊 탭1 - 시도별 총/연령구간
    with tab1:
        st.subheader("시도별 총인구수 및 연령구간인구수")
        df_city = df_total.groupby("시도")[["총인구수", "연령구간인구수"]].sum().reset_index()
        option = st.radio("표시할 항목", ["총인구수", "연령구간인구수"], horizontal=True)
        fig = px.bar(df_city, x="시도", y=option, title=f"{option} (시도별)", text_auto=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # 📈 탭2 - 연령별 인구 분포
    with tab2:
        st.subheader("행정구역별 연령별 인구 분포")
        selected_region = st.selectbox("행정구역 선택", df_total["행정구역"].unique(), key="age_tab")
        row = df_total[df_total["행정구역"] == selected_region].iloc[0]
        df_age = pd.DataFrame({
            "연령": [col.split("_")[-1] for col in age_cols],
            "인구수": [row[col] for col in age_cols]
        })
        fig2 = px.line(df_age, x="연령", y="인구수", markers=True,
                       title=f"{selected_region} 연령별 인구 분포", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    # 👥 탭3 - 남녀 인구 분포
    with tab3:
        st.subheader("행정구역별 연령별 남녀 인구 분포")
        selected_region = st.selectbox("행정구역 선택", df_gender["행정구역"].unique(), key="gender_tab")
        row = df_gender[df_gender["행정구역"] == selected_region].iloc[0]

        male = [row[col] for col in male_cols]
        female = [row[col] for col in female_cols]
        ages = [col.split("_")[-1] for col in male_cols]

        df_gender_plot = pd.DataFrame({
            "연령": ages,
            "남성": male,
            "여성": female
        })

        df_melted = df_gender_plot.melt(id_vars="연령", var_name="성별", value_name="인구수")
        fig3 = px.line(df_melted, x="연령", y="인구수", color="성별", markers=True,
                       title=f"{selected_region} 연령별 남녀 인구 분포", template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
