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


# 장소명으로 후보 리스트 가져오기
def search_locations(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 5}
    headers = {"User-Agent": "my-bookmark-app"}
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    return results


# 북마크 삭제
def delete_bookmark(index):
    bookmarks = load_bookmarks()
    if 0 <= index < len(bookmarks):
        del bookmarks[index]
        save_bookmarks(bookmarks)


# Streamlit 설정
st.set_page_config(page_title="북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

with st.sidebar:
    st.header("🔍 장소 검색 및 추가")
    query = st.text_input("장소 검색")
    search_results = []
    selected_result = None

    if query:
        search_results = search_locations(query)
        if search_results:
            options = [f"{r['display_name']} ({r['lat']}, {r['lon']})" for r in search_results]
            selected_option = st.selectbox("검색 결과", options)
            selected_index = options.index(selected_option)
            selected_result = search_results[selected_index]
        else:
            st.info("검색 결과가 없습니다.")

    desc = st.text_area("설명")

    if selected_result:
        if st.button("➕ 북마크 추가"):
            lat = float(selected_result["lat"])
            lon = float(selected_result["lon"])
            name = selected_result["display_name"]
            if desc:
                bookmarks = load_bookmarks()
                bookmarks.append({
                    "name": name,
                    "desc": desc,
                    "lat": lat,
                    "lon": lon
                })
                save_bookmarks(bookmarks)
                st.success("북마크 저장 완료!")
            else:
                st.warning("설명을 입력해주세요.")

    st.markdown("---")
    st.header("📚 저장된 북마크")

    bookmarks = load_bookmarks()
    for i, bm in enumerate(bookmarks):
        with st.expander(f"{i+1}. {bm['name']}"):
            st.markdown(f"**설명:** {bm['desc']}")
            st.markdown(f"**위치:** ({bm['lat']}, {bm['lon']})")
            if st.button(f"❌ 삭제", key=f"delete_{i}"):
                delete_bookmark(i)
                st.experimental_rerun()

# 지도 생성
map_center = [37.5665, 126.9780]
if bookmarks:
    map_center = [bookmarks[-1]["lat"], bookmarks[-1]["lon"]]

m = folium.Map(location=map_center, zoom_start=12)

# 저장된 북마크 마커 표시
for bm in bookmarks:
    folium.Marker(
        [bm["lat"], bm["lon"]],
        popup=f"<b>{bm['name']}</b><br>{bm['desc']}",
        tooltip=bm["name"]
    ).add_to(m)

# 선택된 검색 결과 미리보기 마커 표시
if selected_result:
    lat = float(selected_result["lat"])
    lon = float(selected_result["lon"])
    folium.Marker(
        [lat, lon],
        popup="미리보기 장소",
        tooltip="🧭 미리보기",
        icon=folium.Icon(color="green")
    ).add_to(m)
    m.location = [lat, lon]
    m.zoom_start = 14

# 지도 렌더링
st_data = st_folium(m, width=1000, height=600)
