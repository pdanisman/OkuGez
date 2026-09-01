import math
import re
import json
import requests

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# ============================================================
# GEZGİN KARAVANLAR — 4. SINIF OKUMA MACERASI
# ============================================================

st.set_page_config(
    page_title="Gezgin Karavanlar | Okuma Macerası",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# CONFIG & API
# ----------------------------
MAPTILER_API_KEY = "EpjYdmP1Sas39ynJVbrR"

STUDENT_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=0&single=true&output=csv"
BOOK_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=1390307822&single=true&output=csv"
RECORD_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=509265349&single=true&output=csv"

# ----------------------------
# THEME (FORCE LIGHT MODE & UX)
# ----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap');

/* Force Light Theme Colors */
.stApp { background: linear-gradient(180deg, #f5eddb 0%, #fffaf0 34%, #fffaf0 100%) !important; }
h1, h2, h3, h4, h5, h6, p, span, div, label, li { color: #2b3744 !important; font-family: 'Nunito', sans-serif; }

.block-container { max-width: 1450px; padding-top: 1.0rem; padding-bottom: 2.5rem; }

/* Hero Section */
.hero {
  position: relative; overflow:hidden; border-radius: 30px; padding: 26px 34px 28px;
  background: radial-gradient(circle at 86% 20%, rgba(255,255,255,.55) 0 7%, transparent 7.3%),
              linear-gradient(135deg, #f8dcae 0%, #f4c989 42%, #eed79d 100%);
  border: 2px solid #dfbd80; box-shadow: 0 12px 35px rgba(81,57,28,.12); margin-bottom: 18px;
}
.hero h1 { font-family:'Baloo 2', sans-serif !important; font-size:44px; line-height:1; margin:0; font-weight:800; }
.hero p { color:#6b5739 !important; font-size:17px; font-weight:700; margin:8px 0 0; }
.eyebrow { color:#8d6a38 !important; font-weight:800; letter-spacing:2px; text-transform:uppercase; font-size:13px; }

/* Cards & Layout */
.card { background:rgba(255,255,255,.95); border:1.5px solid #e5d7bc; border-radius:22px; padding:18px; box-shadow:0 8px 24px rgba(82,60,30,.08); height:100%; display:flex; flex-direction:column; }
.metric-card { text-align: center; justify-content: center; align-items: center; }
.metric-number { font-family:'Baloo 2', sans-serif !important; font-size:38px; font-weight:800; line-height:1.0; }
.metric-label { color:#717782 !important; font-size:14px; font-weight:800; margin-top:5px; text-transform:uppercase; letter-spacing:1px; }

/* Typography & Elements */
.section-title { font-family:'Baloo 2' !important; font-size:28px; font-weight:800; margin: 8px 0 8px; }
.small-muted { color:#7c8088 !important; font-size:13px; }

/* Progress Bar */
.progress-shell { background:#ece2ce; height:16px; border-radius:999px; overflow:hidden; margin-top:12px; width:100%; }
.progress-bar { height:100%; border-radius:999px; background:linear-gradient(90deg,#df9a55,#e4b45a,#7da27a); }

/* Badges */
.badge { border-radius:18px; padding:15px; text-align:center; background:linear-gradient(145deg, #ffffff, #fffaf0); border:2px solid #e7dac1; height:100%; box-shadow: 0 4px 15px rgba(217, 164, 65, 0.15); transition: transform 0.2s; }
.badge:hover { transform: translateY(-5px); }
.badge .emoji { font-size:36px; margin-bottom:5px; }
.badge b { display:block; margin-top:3px; font-size:16px; }

/* Book Cards */
.book-card { display:flex; gap:14px; align-items:center; padding:15px; background:#fffdf7; border:1.5px solid #e9ddc8; border-radius:18px; margin-bottom:12px; transition: 0.2s; }
.book-card:hover { background:#ffffff; box-shadow:0 6px 15px rgba(50,40,20,.10); border-color:#dcb97f; }
.book-cover { width:54px; height:70px; border-radius:9px; display:flex; align-items:center; justify-content:center; color:#fff !important; font-size:22px; font-weight:800; box-shadow:0 4px 10px rgba(0,0,0,.15); flex:0 0 auto; }
.book-card h4 { margin:0; font-size:17px; font-weight:700; }
.book-card p { margin:2px 0; color:#7a7f86 !important; font-size:13px; }

/* Map Markers & Control Styling */
.emoji-marker { display:flex; align-items:center; justify-content:center; width:32px; height:32px; background:rgba(255,255,255,0.95); border:2px solid #e88942; border-radius:50%; box-shadow:0 3px 8px rgba(0,0,0,0.2); font-size:18px; }
.caravan-marker svg { display:block; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.3)); }
.leaflet-control-layers { border: 2px solid #e5d7bc !important; border-radius: 12px !important; background: rgba(255,250,240,.95) !important; box-shadow: 0 4px 12px rgba(82,60,30,.15) !important; font-family: 'Nunito', sans-serif !important; font-weight: 700 !important; color: #2b3744 !important; padding: 5px !important;}

.footer-note { color:#8b806c !important; font-size:13px; text-align:center; padding:22px 0 10px; font-weight:600;}
[data-testid="stSidebar"] { background:#f4ebd8 !important; border-right:1px solid #e2d0ae; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------
# DATA HELPERS
# ----------------------------
def clean_col(name: str) -> str:
    name = str(name).strip()
    name = name.replace("İ", "I").replace("ı", "i")
    name = re.sub(r"\s+", "_", name)
    return name

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [clean_col(c) for c in df.columns]
    return df

def first_existing(df: pd.DataFrame, names, default=None):
    for n in names:
        key = clean_col(n)
        if key in df.columns:
            return key
    return default

@st.cache_data(ttl=60, show_spinner=False)
def load_data():
    students = normalize_columns(pd.read_csv(STUDENT_URL))
    books = normalize_columns(pd.read_csv(BOOK_URL))
    records = normalize_columns(pd.read_csv(RECORD_URL))

    s_no = first_existing(students, ["Ogrenci_No", "Öğrenci_No", "No", "Öğrenci"])
    s_name = first_existing(students, ["Ad_Soyad", "Ogrenci_Adi", "Öğrenci_Adı", "Adı_Soyadı", "İsim"])
    s_color = first_existing(students, ["Karavan_Rengi", "KaravanRengi", "Renk"])
    
    students[s_no] = students[s_no].astype(str).str.strip()
    students["_name"] = students[s_name].astype(str).str.strip() if s_name else students[s_no]
    students["_color"] = students[s_color].astype(str).str.strip() if s_color else "Turuncu"
    students["_no"] = students[s_no]

    b_title = first_existing(books, ["Kitap_Adi_Sehir", "Kitap_Adi", "Kitap"])
    b_lat = first_existing(books, ["Enlem", "Lat", "Latitude"])
    b_lon = first_existing(books, ["Boylam", "Lon", "Longitude"])
    b_km = first_existing(books, ["Sayfa_Sayisi_KM", "Sayfa_KM", "KM", "Sayfa"])
    b_kind = first_existing(books, ["Tur", "Tür", "Kategori"])
    b_cont = first_existing(books, ["Kita", "Kıta"])
    b_emoji = first_existing(books, ["Ikon", "İkon", "Emoji"])

    books[b_title] = books[b_title].astype(str).str.strip()
    books["_title"] = books[b_title]
    books["_lat"] = pd.to_numeric(books[b_lat], errors="coerce") if b_lat else np.nan
    books["_lon"] = pd.to_numeric(books[b_lon], errors="coerce") if b_lon else np.nan
    books["_km"] = pd.to_numeric(books[b_km], errors="coerce").fillna(0) if b_km else 0
    books["_kind"] = books[b_kind].astype(str).str.strip() if b_kind else "Genel"
    books["_continent"] = books[b_cont].astype(str).str.strip() if b_cont else "Avrupa"
    books["_emoji"] = books[b_emoji].astype(str).str.strip() if b_emoji else "📚"

    r_no = first_existing(records, ["Ogrenci_No", "Öğrenci_No", "No"])
    r_book = first_existing(records, ["Okudugu_Kitap", "Okuduğu_Kitap", "Kitap", "Kitap_Adi"])
    
    records["_no"] = records[r_no].astype(str).str.strip()
    records["_book"] = records[r_book].astype(str).str.strip()
    
    return students, books, records

COLORS = {
    "Macera": (222, 145, 77), "Gizem": (113, 122, 171), "Fantastik": (140, 105, 171),
    "Mizah": (221, 157, 78), "Bilim": (76, 144, 170), "Doğa": (103, 154, 105),
    "Tarih": (170, 125, 74), "Klasik": (180, 108, 120), "Genel": (128, 128, 128),
}

CONTINENT_STYLE = {
    "Avrupa": {"fill": "#efc79c"}, "Asya": {"fill": "#bed7e4"}, "Afrika": {"fill": "#bfd3a9"},
    "Kuzey Amerika": {"fill": "#e8bdc8"}, "Güney Amerika": {"fill": "#c6d6bd"}, "Okyanusya": {"fill": "#c8cce2"},
}

def color_for_kind(kind):
    k = str(kind).lower()
    for key, rgb in COLORS.items():
        if key.lower() in k: return rgb
    return COLORS["Genel"]

def rgba_hex(rgb):
    return '#%02x%02x%02x' % rgb

# ----------------------------
# CARAVAN ENGINE
# ----------------------------
def caravan_stage(km: float):
    stages = [
        (0, "Minik Kaşif", "🚶", "İlk Adım"),
        (500, "Gezgin", "🚐", "Yola Çıktı"),
        (1000, "Yol Arkadaşı", "🏕️", "Kampçı"),
        (2000, "Usta Gezgin", "🚌", "Büyük Karavan"),
        (5000, "Kıta Kaşifi", "🚙", "Keşif Karavanı"),
        (10000, "Dünya Kaşifi", "🚀", "Yıldız Karavanı"),
        (20000, "Efsane Kaşif", "🌟", "Efsanevi Karavan"),
    ]
    current = stages[0]
    next_km = stages[1][0]
    for i, item in enumerate(stages):
        if km >= item[0]:
            current = item
            next_km = stages[i + 1][0] if i + 1 < len(stages) else item[0]
    remaining = max(0, next_km - km)
    return current[1], current[2], current[3], remaining, current[0]

def caravan_svg(km, color_hex="#e88942", size=78):
    name, emoji, _, _, stage_km = caravan_stage(km)
    stage = sum(1 for t in [0, 500, 1000, 2000, 5000, 10000, 20000] if km >= t)
    
    if stage == 1:
        body = f'<circle cx="49" cy="31" r="13" fill="{color_hex}"/><circle cx="49" cy="31" r="6" fill="#fff4d4"/>'
        wheel = ''
    elif stage == 2:
        body = f'<rect x="28" y="20" rx="11" width="44" height="31" fill="{color_hex}"/><path d="M30 36h40" stroke="#fff7df" stroke-width="4"/>'
        wheel = '<circle cx="38" cy="54" r="5" fill="#30414e"/><circle cx="64" cy="54" r="5" fill="#30414e"/>'
    elif stage in (3,4):
        body = f'<path d="M23 48V28c0-7 5-12 12-12h26c6 0 10 3 14 9l7 15v8H23z" fill="{color_hex}"/><rect x="55" y="22" width="20" height="15" rx="4" fill="#e8f1ed" opacity=".9"/>'
        wheel = '<circle cx="37" cy="52" r="7" fill="#30414e"/><circle cx="73" cy="52" r="7" fill="#30414e"/>'
    elif stage in (5,6):
        body = f'<path d="M18 47V27c0-7 6-12 13-12h32c8 0 13 5 17 12l9 20H18z" fill="{color_hex}"/><path d="M44 17v28" stroke="#fff7df" stroke-width="3"/><rect x="52" y="22" width="22" height="13" rx="3" fill="#eaf3f6"/>'
        wheel = '<circle cx="34" cy="52" r="7" fill="#30414e"/><circle cx="77" cy="52" r="7" fill="#30414e"/><circle cx="98" cy="52" r="7" fill="#30414e"/>'
    else:
        body = f'<path d="M16 43c14-23 28-29 49-29 17 0 28 8 38 23h14v8H16z" fill="{color_hex}"/><path d="M32 25c8-8 14-10 23-10 12 0 22 4 29 10" fill="none" stroke="#fff6d8" stroke-width="3"/>'
        wheel = '<circle cx="34" cy="50" r="8" fill="#30414e"/><circle cx="83" cy="50" r="8" fill="#30414e"/><circle cx="110" cy="50" r="8" fill="#30414e"/>'
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{int(size*0.72)}" viewBox="0 0 130 70">
      <defs><filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity=".3"/></filter></defs>
      <g filter="url(#s)">{body}{wheel}<path d="M8 56h110" stroke="#8a714b" stroke-width="2" stroke-linecap="round" stroke-dasharray="4 5"/><circle cx="16" cy="56" r="3" fill="#d9a441"/></g>
      <text x="65" y="67" text-anchor="middle" font-family="Nunito" font-size="8" font-weight="800" fill="#5e5343">{stage_km:,}+</text>
    </svg>'''
    return svg

def html_caravan_icon(km, color):
    return f'<div class="caravan-marker">{caravan_svg(km, color)}</div>'

# ----------------------------
# ROUTES
# ----------------------------
def smooth_curve(a, b, bends=18):
    lat1, lon1 = a; lat2, lon2 = b
    points = []
    dx = lon2 - lon1; dy = lat2 - lat1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    bend = min(9.0, max(1.3, length * 0.08))
    c1 = ((lat1 + lat2) / 2 + ny * bend, (lon1 + lon2) / 2 + nx * bend)
    for t in np.linspace(0, 1, bends):
        lat = (1-t)**2 * lat1 + 2*(1-t)*t*c1[0] + t**2 * lat2
        lon = (1-t)**2 * lon1 + 2*(1-t)*t*c1[1] + t**2 * lon2
        points.append([lat, lon])
    return points

# ----------------------------
# APP DATA
# ----------------------------
try:
    students, books, records = load_data()
    data_error = None
except Exception as exc:
    students, books, records = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    data_error = str(exc)

st.sidebar.markdown("# 🧭 Gezgin Karavanlar")
st.sidebar.caption("4. Sınıf Okuma Macerası")
page = st.sidebar.radio("Menü", ["🌍 Dünya Haritası", "🎒 Kaşiflerim", "📚 Kitaplık", "📊 Sınıf Günlüğü"])
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri yenile", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
st.sidebar.info("Her kitap kaydı eklendiğinde rota, kilometre, unvan ve karavan seviyesi otomatik güncellenir.")

if data_error:
    st.error(f"Veriler okunamadı: {data_error}")
    st.stop()

book_map = {str(r["_title"]): r for _, r in books.iterrows()}
records = records[records["_book"].isin(book_map.keys())].copy()
records = records.merge(books[["_title", "_lat", "_lon", "_km", "_kind", "_continent", "_emoji"]], left_on="_book", right_on="_title", how="left")
records = records.sort_values(["_no", "_book"])

student_totals = records.groupby("_no")["_km"].sum().to_dict()
students["_km"] = students["_no"].map(student_totals).fillna(0)
students["_book_count"] = students["_no"].map(records["_no"].value_counts()).fillna(0).astype(int)

class_km = int(records["_km"].sum()) if not records.empty else 0
class_books = int(len(records))

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">4. SINIF · Borsa İstanbul Şükran Ana İlkokulu</div>
      <h1>📚 Kitaplarla Dünyayı Keşfediyoruz</h1>
      <p>Her kitap bir durak. Her sayfa bir yolculuk. Her çocuk kendi macerasının kaşifi. 🧭</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# PAGE: DÜNYA HARİTASI
# ----------------------------
if page == "🌍 Dünya Haritası":
    st.title("🌍 Gezgin Karavanlar Dünya Haritası")
    
    # Zarif 3'lü Filtreleme
    c1, c2, c3 = st.columns([1.1, 1.0, 1.2])
    with c1:
        selected_student = st.selectbox("👤 Kaşif Seçin", ["Sınıfın tamamı"] + list(students["_name"].astype(str)))
    with c2:
        selected_kind = st.selectbox("📖 Kitap Türü", ["Tüm türler"] + sorted([x for x in books["_kind"].dropna().unique() if str(x).strip()]))
    with c3:
        selected_title = st.selectbox("📍 Kitap Durağı", ["Tüm kitaplar"] + sorted(books["_title"].dropna().astype(str).tolist()))

    # UX MÜDAHALESİ: Akıllı Rota Gösterimi
    # Eğer tüm sınıf seçiliyse göz yormaması için çizgiler kapalı gelir, şık bir sürgü ile açılabilir.
    # Tek bir çocuk seçiliyse sürgü gizlenir, sistem rotayı otomatik çizer.
    if selected_student == "Sınıfın tamamı":
        st.markdown("<div style='margin-top: 5px; margin-bottom: -15px;'></div>", unsafe_allow_html=True)
        show_routes = st.toggle("🗺️ Tüm Sınıfın Rota Ağını Göster", value=False)
    else:
        show_routes = True # Tek çocukta sürgü yok, rota hep açık.

    filtered_books = books.copy()
    if selected_kind != "Tüm türler":
        filtered_books = filtered_books[filtered_books["_kind"].str.contains(selected_kind, case=False, na=False)]
    if selected_title != "Tüm kitaplar":
        filtered_books = filtered_books[filtered_books["_title"] == selected_title]

    if selected_student != "Sınıfın tamamı":
        student_no_selected = students[students["_name"] == selected_student].iloc[0]["_no"]
        class_student_records = records[records["_no"] == student_no_selected].copy()
    else:
        class_student_records = records.copy()

    # Harita Altyapısı (Aquarelle)
    tiles_url = f"https://api.maptiler.com/maps/aquarelle-v4/256/{{z}}/{{x}}/{{y}}.png?key={MAPTILER_API_KEY}"
    m = folium.Map(location=[24, 15], zoom_start=2.35, min_zoom=1.7, max_zoom=7, tiles=tiles_url, attr="MapTiler", control_scale=True)

    # Kıtalar GeoJSON
    GEOJSON_URL = "https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/f3fde312c9b8168af6254ce1410dd4dda4a31941/continents.json"
    def style_function(feature):
        c_name = feature['properties'].get('CONTINENT', '')
        name_map = {"Europe": "Avrupa", "Asia": "Asya", "Africa": "Afrika", "North America": "Kuzey Amerika", "South America": "Güney Amerika", "Oceania": "Okyanusya"}
        tr_name = name_map.get(c_name, "")
        fill_color = CONTINENT_STYLE.get(tr_name, {}).get("fill", "#e0e0e0")
        return {'fillColor': fill_color, 'color': 'transparent', 'weight': 0, 'fillOpacity': 0.4}

    try:
        geo_data = requests.get(GEOJSON_URL, verify=False, timeout=5).json()
        folium.GeoJson(geo_data, name="Kıtalar", style_function=style_function).add_to(m)
    except:
        pass

    # Kitap Durakları
    for _, row in filtered_books.iterrows():
        if pd.isna(row["_lat"]) or pd.isna(row["_lon"]): continue
        rgb = color_for_kind(row["_kind"])
        border_color = rgba_hex(rgb)
        
        icon_html = f'<div class="emoji-marker" style="border-color: {border_color};">{row["_emoji"]}</div>'
        popup_html = f"<div style='font-family:Nunito'><b>{row['_title']}</b><br>🌈 Tür: {row['_kind']}<br>🗺️ Kıta: {row['_continent']}<br>📄 Yolculuk: {int(row['_km'])} km</div>"
        
        folium.Marker(
            [row["_lat"], row["_lon"]],
            icon=folium.DivIcon(html=icon_html, icon_anchor=(16, 16)),
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["_title"],
        ).add_to(m)

    # Karavanlar ve Rotalar
    if not class_student_records.empty:
        for student_no, group in class_student_records.groupby("_no"):
            student_row = students[students["_no"] == student_no].iloc[0]
            
            color_map = {"Mavi":"#4f88bd","Turuncu":"#df8b43","Mor":"#8c72a8","Kırmızı":"#c85d63","Yeşil":"#6d9b69","Sarı":"#d9a441"}
            caravan_color = color_map.get(str(student_row["_color"]).title(), "#df8b43")
            
            route_points = []
            ordered = group.dropna(subset=["_lat","_lon"]).copy()
            if not ordered.empty:
                previous = None
                for _, book_row in ordered.iterrows():
                    current = [float(book_row["_lat"]), float(book_row["_lon"])]
                    if previous:
                        route_points.extend(smooth_curve(previous, current))
                    else:
                        route_points.append(current)
                    previous = current

                # Rota Çizimi (Sadece şalter açıksa veya tek çocuk seçiliyse)
                if len(route_points) > 1 and show_routes:
                    is_all = (selected_student == "Sınıfın tamamı")
                    folium.PolyLine(
                        route_points, color=caravan_color,
                        weight=2 if is_all else 6, opacity=0.4 if is_all else 0.8,
                        dash_array="4 8" if is_all else None, line_cap="round"
                    ).add_to(m)

                last = ordered.iloc[-1]
                km = float(student_row["_km"])
                title, _, role, remain, _ = caravan_stage(km)
                
                popup_text = f"<div style='font-family:Nunito;min-width:180px'><b>🧭 {student_row['_name']}</b><br>🏆 {title}<br>🌍 {int(km):,} km<br>📍 Son Durak: {last['_title']}</div>"
                
                folium.Marker(
                    [float(last["_lat"]), float(last["_lon"])],
                    popup=folium.Popup(popup_text, max_width=250),
                    tooltip=f"{student_row['_name']} ({int(km):,} km)",
                    icon=folium.DivIcon(html=html_caravan_icon(km, caravan_color), icon_size=(92,60), icon_anchor=(46,30)),
                ).add_to(m)

    st_folium(m, width=None, height=650, returned_objects=[])

# ----------------------------
# PAGE: KAŞİFLERİM
# ----------------------------
elif page == "🎒 Kaşiflerim":
    st.markdown('<div class="section-title">🎒 Kaşiflerim</div>', unsafe_allow_html=True)
    search = st.text_input("🔎 Öğrenci ara", placeholder="İsim yazın...")
    
    view_df = students.copy()
    if search.strip():
        view_df = view_df[view_df["_name"].str.contains(search.strip(), case=False, na=False)]

    cols = st.columns(3)
    for i, (_, row) in enumerate(view_df.sort_values("_km", ascending=False).iterrows()):
        with cols[i % 3]:
            km = float(row["_km"])
            name, emoji, role, remain, threshold = caravan_stage(km)
            pct = 100 if remain == 0 else min(100, max(0, (km-threshold) / max(1, (km-remain)-threshold) * 100))
            svg_color = {"Mavi":"#4f88bd","Turuncu":"#df8b43","Mor":"#8c72a8","Kırmızı":"#c85d63","Yeşil":"#6d9b69"}.get(str(row["_color"]).title(), "#df8b43")
            
            st.markdown(
                f'''<div class="card" style="margin-bottom:20px;">
                <div style="display:flex;justify-content:space-between">
                    <div><div class="eyebrow">KAŞİF</div><div style="font-family:Baloo 2;font-weight:800;font-size:22px;">{row['_name']}</div></div>
                    <div style="font-size:32px">{emoji}</div>
                </div>
                <div style="margin:10px 0;">{caravan_svg(km, svg_color, size=90)}</div>
                <div style="font-weight:800;font-size:18px;">🏆 {name}</div>
                <div class="small-muted">{role} · {int(km):,} km · {int(row['_book_count'])} kitap</div>
                <div class="progress-shell"><div class="progress-bar" style="width:{min(100,pct):.1f}%"></div></div>
                <div class="small-muted" style="margin-top:5px">Sonraki seviyeye {int(remain):,} km</div>
                </div>''',
                unsafe_allow_html=True
            )

# ----------------------------
# PAGE: KİTAPLIK
# ----------------------------
elif page == "📚 Kitaplık":
    st.markdown('<div class="section-title">📚 Dünya Okur Kütüphanesi</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    unique_kinds = sorted(list(set(k.strip() for sublist in books["_kind"].dropna().astype(str).str.split(',') for k in sublist if k.strip())))
    with c1:
        kind = st.selectbox("Tür Filtresi", ["Tümü"] + unique_kinds)
    with c2:
        cont = st.selectbox("Kıta Filtresi", ["Tümü"] + sorted(books["_continent"].dropna().astype(str).unique().tolist()))
    
    lib = books.copy()
    if kind != "Tümü":
        lib = lib[lib["_kind"].str.contains(kind, case=False, na=False)]
    if cont != "Tümü":
        lib = lib[lib["_continent"].str.contains(cont, case=False, na=False)]

    read_counts = records["_book"].value_counts().to_dict()
    book_cols = st.columns(2)
    for i, (_, row) in enumerate(lib.sort_values("_title").iterrows()):
        rgb = color_for_kind(row["_kind"])
        cover = rgba_hex(rgb)
        count = int(read_counts.get(row["_title"], 0))
        with book_cols[i % 2]:
            st.markdown(
                f'''<div class="book-card"><div class="book-cover" style="background:{cover}">{row['_emoji']}</div>
                <div><h4>{row['_title']}</h4><p>{row['_kind']} · {row['_continent']} · {int(row['_km'])} km</p>
                <p style="color:#df8b43 !important; font-weight:700;">👣 {count} kaşif ziyaret etti</p></div></div>''',
                unsafe_allow_html=True,
            )

# ----------------------------
# PAGE: SINIF GÜNLÜĞÜ
# ----------------------------
elif page == "📊 Sınıf Günlüğü":
    st.markdown('<div class="section-title">📊 Sınıf Okuma Günlüğü</div>', unsafe_allow_html=True)
    if records.empty:
        st.info("Kayıt bulunamadı. İlk kitap okunduğunda veriler burada belirecektir.")
        st.stop()

    popular_book = records["_book"].value_counts().index[0] if not records.empty else "—"
    top_student = students.sort_values("_km", ascending=False).iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    metrics = [(f"{class_km:,}", "Dünya Etrafında KM"), (f"{class_books}", "Okunan Kitap"), (popular_book, "Popüler Durak"), (f"{top_student['_name']}", "Lider Kaşif")]
    for col, (n,l) in zip([c1,c2,c3,c4], metrics):
        with col:
            font_sz = 26 if len(str(n)) > 12 else 34
            st.markdown(f'<div class="card metric-card"><div class="metric-number" style="font-size:{font_sz}px">{n}</div><div class="metric-label">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)
    
    with left:
        st.markdown("#### 🏆 En Çok Ziyaret Edilen Duraklar")
        top_books = records["_book"].value_counts().head(5).reset_index()
        top_books.columns = ["Kitap", "Ziyaret"]
        fig3 = px.bar(top_books, x="Ziyaret", y="Kitap", orientation="h", color="Ziyaret", color_continuous_scale="Oryel")
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            yaxis={'categoryorder':'total ascending', 'title': None},
            xaxis={'title': 'Ziyaret Sayısı'},
            font=dict(color="#2b3744", family="Nunito", size=13),
            coloraxis_showscale=False # Sağdaki gereksiz renk çubuğunu gizler, grafiğe yer açar
        )
        st.plotly_chart(fig3, use_container_width=True, theme=None)

    with right:
        st.markdown("#### 🧭 En Çok KM Yapan Kaşifler")
        rank = students[["_name","_km"]].sort_values("_km", ascending=False).head(5)
        fig2 = px.bar(rank, x="_km", y="_name", orientation="h", color="_km", color_continuous_scale="Teal")
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            yaxis={'categoryorder':'total ascending', 'title': None},
            xaxis={'title': 'Yapılan Kilometre'},
            font=dict(color="#2b3744", family="Nunito", size=13),
            coloraxis_showscale=False # Sağdaki gereksiz renk çubuğunu gizler, grafiğe yer açar
        )
        st.plotly_chart(fig2, use_container_width=True, theme=None)

    st.markdown("#### 🏅 Kazanılan Sınıf Rozetleri")
    badges = [
        ("📖", "İlk Kitap", int((students["_book_count"] >= 1).sum())),
        ("🧭", "500 KM Kaşifi", int((students["_km"] >= 500).sum())),
        ("🌍", "1.000 KM Gezgini", int((students["_km"] >= 1000).sum())),
        ("🚀", "5.000 KM Kıta", int((students["_km"] >= 5000).sum())),
        ("🌟", "10.000 KM Efsane", int((students["_km"] >= 10000).sum())),
    ]
    badge_cols = st.columns(len(badges))
    for col, (emo, label, count) in zip(badge_cols, badges):
        with col:
            st.markdown(f'<div class="badge"><div class="emoji">{emo}</div><b>{label}</b><span class="small-muted">{count} öğrenci rozeti aldı</span></div>', unsafe_allow_html=True)
