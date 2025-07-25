import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

# JSON 파일 경로
BOOKMARK_FILE = "bookmarks.json"

# 북마크 불러오기
def load_bookmarks():
    if os.path.exists(BOOKMARK_FILE):
        with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 북마크 저장하기
def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)

# 앱 UI
st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

with st.sidebar:
    st.header("➕ 장소 추가하기")
    name = st.text_input("장소 이름")
    desc = st.text_area("설명")
    lat = st.number_input("위도 (Latitude)", format="%.6f")
    lon = st.number_input("경도 (Longitude)", format="%.6f")

    if st.button("북마크 추가"):
        if name and desc:
            new = {"name": name, "desc": desc, "lat": lat, "lon": lon}
            data = load_bookmarks()
            data.append(new)
            save_bookmarks(data)
            st.success("북마크가 추가되었습니다.")
        else:
            st.warning("장소 이름과 설명을 입력해주세요.")

    st.markdown("---")
    st.header("📚 북마크 목록")

    for i, bm in enumerate(load_bookmarks()):
        st.markdown(f"**{i+1}. {bm['name']}**  \n{bm['desc']}  \n({bm['lat']}, {bm['lon']})")

# 지도 표시
map_center = [37.5665, 126.9780]  # 기본 서울 위치
bookmarks = load_bookmarks()
if bookmarks:
    last = bookmarks[-1]
    map_center = [last["lat"], last["lon"]]

m = folium.Map(location=map_center, zoom_start=12)
for bm in bookmarks:
    folium.Marker(
        [bm["lat"], bm["lon"]],
        popup=f"<b>{bm['name']}</b><br>{bm['desc']}",
        tooltip=bm["name"]
    ).add_to(m)

st_data = st_folium(m, width=1000, height=600)
