import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import requests

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

# 장소명으로 위도/경도 검색
def search_location(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "my-bookmark-app"
    }
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"])
    return None, None

# Streamlit 설정
st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

# 사이드바 - 북마크 추가
with st.sidebar:
    st.header("🔍 장소 검색 및 북마크")
    name = st.text_input("장소 이름 (예: 서울시청, Eiffel Tower 등)")
    desc = st.text_area("설명")

    if st.button("🔎 검색 후 북마크 저장"):
        if name and desc:
            lat, lon = search_location(name)
            if lat and lon:
                bookmarks = load_bookmarks()
                bookmarks.append({"name": name, "desc": desc, "lat": lat, "lon": lon})
                save_bookmarks(bookmarks)
                st.success(f"✅ {name} 저장 완료! ({lat:.5f}, {lon:.5f})")
            else:
                st.error("❌ 장소를 찾을 수 없습니다.")
        else:
            st.warning("⚠️ 장소 이름과 설명을 모두 입력해주세요.")

    st.markdown("---")
    st.header("📚 저장된 북마크")
    for i, bm in enumerate(load_bookmarks()):
        st.markdown(f"**{i+1}. {bm['name']}**  \n{bm['desc']}  \n({bm['lat']}, {bm['lon']})")

# 지도 생성
bookmarks = load_bookmarks()
map_center = [37.5665, 126.9780]  # 기본 서울
if bookmarks:
    map_center = [bookmarks[-1]["lat"], bookmarks[-1]["lon"]]

m = folium.Map(location=map_center, zoom_start=12)
for bm in bookmarks:
    folium.Marker(
        [bm["lat"], bm["lon"]],
        popup=f"<b>{bm['name']}</b><br>{bm['desc']}",
        tooltip=bm["name"]
    ).add_to(m)

st_data = st_folium(m, width=1000, height=600)
