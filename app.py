import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 로딩 함수
@st.cache_data
def load_data():
    df_total = pd.read_csv("202506_202506_연령별인구현황_월간_합계.csv", encoding="cp949")
    df_gender = pd.read_csv("202506_202506_연령별인구현황_월간_남녀구분.csv", encoding="cp949")
    return df_total, df_gender

# 데이터 전처리 함수
def preprocess(df, title):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")]
    df = df.set_index("행정구역")
    df = df.applymap(lambda x: int(str(x).replace(",", "")) if isinstance(x, str) and x.replace(",", "").isdigit() else x)
    df = df.dropna(axis=1, how='any')
    df.index.name = title
    return df

# Streamlit 메인 앱
def main():
    st.set_page_config(page_title="인구 통계 시각화 (Plotly)", layout="wide")
    st.title("📊 2025년 6월 연령별 인구 통계 (Plotly 기반)")

    # 데이터 로딩 및 전처리
    df_total, df_gender = load_data()
    df_total_cleaned = preprocess(df_total, "행정구역")
    df_gender_cleaned = preprocess(df_gender, "행정구역")

    # 탭 구성
    tab1, tab2 = st.tabs(["🔢 합계 인구 (Plotly Bar)", "👫 남녀 인구 (Plotly Line)"])

    with tab1:
        st.subheader("연령별 인구 - 전체")
        selected_area = st.selectbox("행정구역 선택", df_total_cleaned.index, key="total_area")
        row = df_total_cleaned.loc[selected_area]
        df_plot = pd.DataFrame({
            "연령": [col.split("_")[-1] for col in row.index],
            "인구 수": row.values
        })
        fig = px.bar(df_plot, x="연령", y="인구 수", title=f"{selected_area} 연령별 인구 (합계)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("연령별 인구 - 남녀 구분")
        selected_area2 = st.selectbox("행정구역 선택 (남녀)", df_gender_cleaned.index, key="gender_area")

        male = df_gender_cleaned.loc[selected_area2].filter(like="_남_")
        female = df_gender_cleaned.loc[selected_area2].filter(like="_여_")

        df_mf = pd.DataFrame({
            "연령": [col.split("_")[-1] for col in male.index],
            "남성": male.values,
            "여성": female.values
        })

        df_mf_melted = df_mf.melt(id_vars="연령", value_vars=["남성", "여성"], var_name="성별", value_name="인구 수")

        fig2 = px.line(df_mf_melted, x="연령", y="인구 수", color="성별", markers=True, title=f"{selected_area2} 연령별 남녀 인구", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
