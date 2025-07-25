import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict

# 📥 데이터 로딩
@st.cache_data
def load_data():
    df_total = pd.read_csv("202506_202506_연령별인구현황_월간_합계.csv", encoding="cp949")
    df_gender = pd.read_csv("202506_202506_연령별인구현황_월간_남녀구분.csv", encoding="cp949")
    df_econ = pd.read_csv("연령별_경제활동인구_총괄_20250725132144.csv", encoding="utf-8")
    return df_total, df_gender, df_econ

# 🧹 기본 인구 전처리
def preprocess(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")]
    df["시도"] = df["행정구역"].apply(lambda x: x.split()[0])
    df["총인구수"] = df["2025년06월_계_총인구수"].str.replace(",", "").astype(int)
    df["연령구간인구수"] = df["2025년06월_계_연령구간인구수"].str.replace(",", "").astype(int)
    age_cols = [col for col in df.columns if "세" in col and "계" in col]
    for col in age_cols:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)
    return df, age_cols

# 🧹 성별 인구 전처리
def preprocess_gender(df):
    df.columns = df.columns.str.strip()
    df = df.rename(columns={df.columns[0]: "행정구역"})
    df = df[~df["행정구역"].str.contains("소계|계")]
    df["시도"] = df["행정구역"].apply(lambda x: x.split()[0])
    drop_cols = [col for col in df.columns if "총인구수" in col or "연령구간인구수" in col]
    df = df.drop(columns=drop_cols)
    male_cols = [col for col in df.columns if "_남_" in col and "세" in col]
    female_cols = [col for col in df.columns if "_여_" in col and "세" in col]
    for col in male_cols + female_cols:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)
    return df, male_cols, female_cols

# 🧹 실업률/고용률 (연령계층별) 전처리
def preprocess_econ_avg(df):
    cols = [col for col in df.columns if col.endswith(".6") or col.endswith(".7")]
    data_dict = defaultdict(lambda: defaultdict(list))
    for col in cols:
        try:
            year = int(col.split(".")[0])
            code = col.split(".")[-1]
            metric = "실업률" if code == "6" else "고용률"
            for _, row in df.iterrows():
                age_group = row["연령계층별"]
                if pd.isna(age_group) or age_group in ["15세 이상 전체", "15 - 29세", "15 - 64세"]:
                    continue
                if age_group == "15 - 24세":
                    age_group = "청년층 (15-24세)"
                value = pd.to_numeric(row[col], errors="coerce")
                if pd.notna(value):
                    data_dict[(year, age_group, metric)]["값"].append(value)
        except:
            continue
    processed = []
    for key, values in data_dict.items():
        year, age_group, metric = key
        mean_val = sum(values["값"]) / len(values["값"])
        processed.append({
            "연도": year,
            "연령계층": age_group,
            "지표": metric,
            "값": round(mean_val, 2)
        })
    return pd.DataFrame(processed)

# 🧹 실업률/고용률 (15세 이상 전체) 전처리
def preprocess_total_avg(df):
    cols = [col for col in df.columns if col.endswith(".6") or col.endswith(".7")]
    data_dict = defaultdict(list)
    for col in cols:
        try:
            year = int(col.split(".")[0])
            code = col.split(".")[-1]
            metric = "실업률" if code == "6" else "고용률"
            row = df[df["연령계층별"] == "15세 이상 전체"]
            if not row.empty:
                value = pd.to_numeric(row.iloc[0][col], errors="coerce")
                if pd.notna(value):
                    data_dict[(year, metric)].append(value)
        except:
            continue
    result = []
    for (year, metric), vals in data_dict.items():
        result.append({
            "연도": year,
            "지표": metric,
            "값": round(sum(vals) / len(vals), 2)
        })
    return pd.DataFrame(result)

# 🚀 Streamlit 앱 시작
def main():
    st.set_page_config(page_title="인구 + 고용 통계 시각화", layout="wide")
    st.title("📊 인구 및 고용 통계 시각화 대시보드")

    df_total, df_gender, df_econ = load_data()
    df_total, age_cols = preprocess(df_total)
    df_gender, male_cols, female_cols = preprocess_gender(df_gender)
    df_employ = preprocess_econ_avg(df_econ)
    df_total_avg = preprocess_total_avg(df_econ)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ 시도별 총/연령구간 인구",
        "📈 연령별 인구 분포",
        "👥 남녀 인구 분포",
        "💼 연령계층별 실업률/고용률",
        "🧩 전체 실업률/고용률 (15세 이상 전체)"
    ])

    with tab1:
        st.subheader("시도별 총인구수 및 연령구간인구수")
        df_city = df_total.groupby("시도")[["총인구수", "연령구간인구수"]].sum().reset_index()
        option = st.radio("표시할 항목", ["총인구수", "연령구간인구수"], horizontal=True)
        fig = px.bar(df_city, x="시도", y=option, title=f"{option} (시도별)", text_auto=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

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

    with tab3:
        st.subheader("행정구역별 연령별 남녀 인구 분포")
        selected_region = st.selectbox("행정구역 선택", df_gender["행정구역"].unique(), key="gender_tab")
        row = df_gender[df_gender["행정구역"] == selected_region].iloc[0]
        male = [row[col] for col in male_cols]
        female = [row[col] for col in female_cols]
        ages = [col.split("_")[-1] for col in male_cols]
        df_gender_plot = pd.DataFrame({"연령": ages, "남성": male, "여성": female})
        df_melted = df_gender_plot.melt(id_vars="연령", var_name="성별", value_name="인구수")
        fig3 = px.line(df_melted, x="연령", y="인구수", color="성별", markers=True,
                       title=f"{selected_region} 연령별 남녀 인구 분포", template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        st.subheader("💼 연령계층별 연도별 실업률 / 고용률")
        selected_type = st.radio("지표 선택", ["실업률", "고용률"], horizontal=True)
        df_filtered = df_employ[df_employ["지표"] == selected_type]
        fig4 = px.line(df_filtered, x="연도", y="값", color="연령계층", markers=True,
                       title=f"연도별 {selected_type} (연령계층별)", template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)

    with tab5:
        st.subheader("🧩 15세 이상 전체: 연도별 실업률 / 고용률")
        selected_type5 = st.radio("지표 선택", ["실업률", "고용률"], horizontal=True, key="total_tab")
        df_filtered5 = df_total_avg[df_total_avg["지표"] == selected_type5]
        fig5 = px.line(df_filtered5, x="연도", y="값", markers=True,
                       title=f"15세 이상 전체 {selected_type5} 연도별 추이",
                       template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)

if __name__ == "__main__":
    main()
