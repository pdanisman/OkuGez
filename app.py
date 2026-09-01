import math
import re
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from branca.element import Element
from streamlit_folium import st_folium

# ============================================================
# GEZGİN KARAVANLAR — 4. SINIF OKUMA MACERASI
# Streamlit + Google Sheets CSV + Folium
# ============================================================

st.set_page_config(
    page_title="Gezgin Karavanlar | Okuma Macerası",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# CONFIG
# ----------------------------
DEFAULT_URLS = {
    "students": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=0&single=true&output=csv",
    "books": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=1390307822&single=true&output=csv",
    "records": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=509265349&single=true&output=csv",
}

# If you prefer Streamlit secrets, create .streamlit/secrets.toml:
# [data]
# students = "..."
# books = "..."
# records = "..."

def get_url(name: str) -> str:
    try:
        return str(st.secrets["data"][name])
    except Exception:
        return DEFAULT_URLS[name]

STUDENT_URL = get_url("students")
BOOK_URL = get_url("books")
RECORD_URL = get_url("records")

# ----------------------------
# THEME
# ----------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap');
:root {
  --ink: #243447;
  --muted: #6c7480;
  --paper: #fffaf0;
  --cream: #f7efd9;
  --sand: #e9d8b5;
  --orange: #e88942;
  --teal: #4b9a96;
  --green: #6d9b69;
  --purple: #8c72a8;
  --pink: #d67d97;
  --blue: #5d8db8;
  --gold: #d9a441;
}
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: linear-gradient(180deg, #f5eddb 0%, #fffaf0 34%, #fffaf0 100%); }
.block-container { max-width: 1450px; padding-top: 1.0rem; padding-bottom: 2.5rem; }
.hero {
  position: relative; overflow:hidden; border-radius: 30px; padding: 26px 34px 28px;
  background: radial-gradient(circle at 86% 20%, rgba(255,255,255,.55) 0 7%, transparent 7.3%),
              linear-gradient(135deg, #f8dcae 0%, #f4c989 42%, #eed79d 100%);
  border: 2px solid #dfbd80; box-shadow: 0 12px 35px rgba(81,57,28,.12); margin-bottom: 18px;
}
.hero:after { content:'✦   ✧   ✦   ✧'; position:absolute; right:28px; bottom:12px; color:rgba(96,75,43,.23); font-size:32px; letter-spacing:10px; }
.hero h1 { font-family:'Baloo 2', sans-serif; color:#243447; font-size:44px; line-height:1; margin:0; font-weight:800; }
.hero p { color:#6b5739; font-size:17px; font-weight:700; margin:8px 0 0; }
.eyebrow { color:#8d6a38; font-weight:800; letter-spacing:2px; text-transform:uppercase; font-size:13px; }
.card { background:rgba(255,250,240,.92); border:1.5px solid #e5d7bc; border-radius:22px; padding:18px; box-shadow:0 8px 24px rgba(82,60,30,.08); }
.metric-card { min-height:132px; }
.metric-number { font-family:'Baloo 2', sans-serif; font-size:34px; font-weight:800; color:#243447; line-height:1.0; }
.metric-label { color:#717782; font-size:13px; font-weight:800; margin-top:5px; }
.chip { display:inline-block; padding:6px 10px; border-radius:999px; margin:3px 5px 3px 0; font-size:12px; font-weight:800; background:#f0e5cf; color:#6a5538; }
.section-title { font-family:'Baloo 2'; font-size:28px; font-weight:800; color:#243447; margin: 8px 0 8px; }
.small-muted { color:#7c8088; font-size:13px; }
.progress-shell { background:#ece2ce; height:16px; border-radius:999px; overflow:hidden; margin-top:8px; }
.progress-bar { height:100%; border-radius:999px; background:linear-gradient(90deg,#df9a55,#e4b45a,#7da27a); }
.badge { border-radius:18px; padding:13px 12px; text-align:center; background:#fffaf0; border:1.5px solid #e7dac1; height:100%; }
.badge .emoji { font-size:30px; }
.badge b { display:block; margin-top:3px; color:#31404e; }
.book-card { display:flex; gap:14px; align-items:center; padding:12px; background:#fffdf7; border:1.5px solid #e9ddc8; border-radius:18px; margin-bottom:8px; }
.book-cover { width:54px; height:70px; border-radius:9px; display:flex; align-items:center; justify-content:center; color:#fff; font-size:22px; font-weight:800; box-shadow:0 6px 12px rgba(50,40,20,.13); flex:0 0 auto; }
.book-card h4 { margin:0; color:#2b3744; font-size:16px; }
.book-card p { margin:2px 0; color:#7a7f86; font-size:12px; }
.footer-note { color:#8b806c; font-size:12px; text-align:center; padding:22px 0 4px; }
[data-testid="stSidebar"] { background:#f2e7ce; border-right:1px solid #e2d0ae; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-family:'Baloo 2'; color:#334150; }
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

    # Student columns
    s_no = first_existing(students, ["Ogrenci_No", "Öğrenci_No", "No", "Öğrenci"])
    s_name = first_existing(students, ["Ad_Soyad", "Ogrenci_Adi", "Öğrenci_Adı", "Adı_Soyadı", "İsim"])
    s_color = first_existing(students, ["Karavan_Rengi", "KaravanRengi", "Renk"])
    s_spent = first_existing(students, ["Harcanan_Mil", "HarcananMil", "Mil"], None)
    s_img = first_existing(students, ["Karavan_Gorsel_URL", "Karavan_Görsel_URL", "Gorsel_URL", "Görsel_URL"])

    if s_no is None:
        raise ValueError("Öğrenciler tablosunda Ogrenci_No sütunu bulunamadı.")
    students[s_no] = students[s_no].astype(str).str.strip()
    students["_name"] = students[s_name].astype(str).str.strip() if s_name else students[s_no]
    students["_color"] = students[s_color].astype(str).str.strip() if s_color else "Turuncu"
    students["_spent"] = pd.to_numeric(students[s_spent], errors="coerce").fillna(0) if s_spent else 0
    students["_img"] = students[s_img].astype(str).str.strip() if s_img else ""
    students["_no"] = students[s_no]

    # Book columns
    b_title = first_existing(books, ["Kitap_Adi_Sehir", "Kitap_Adi", "Kitap", "Başlık"])
    b_lat = first_existing(books, ["Enlem", "Lat", "Latitude"])
    b_lon = first_existing(books, ["Boylam", "Lon", "Longitude"])
    b_km = first_existing(books, ["Sayfa_Sayisi_KM", "Sayfa_KM", "KM", "Sayfa"])
    b_kind = first_existing(books, ["Tur", "Tür", "Kategori"])
    b_cont = first_existing(books, ["Kita", "Kıta", "Kita_Adi", "Kıta_Adı"])
    b_mix = first_existing(books, ["Tur_Kita", "Tur_Kıta"])
    b_route = first_existing(books, ["Rota_Noktalari", "Rota_Noktaları", "Rota"])
    b_emoji = first_existing(books, ["Ikon", "İkon", "Emoji"])

    if b_title is None:
        raise ValueError("Kitaplar tablosunda Kitap_Adi_Sehir sütunu bulunamadı.")
    books[b_title] = books[b_title].astype(str).str.strip()
    books["_title"] = books[b_title]
    books["_lat"] = pd.to_numeric(books[b_lat], errors="coerce") if b_lat else np.nan
    books["_lon"] = pd.to_numeric(books[b_lon], errors="coerce") if b_lon else np.nan
    books["_km"] = pd.to_numeric(books[b_km], errors="coerce").fillna(0) if b_km else 0
    books["_kind"] = books[b_kind].astype(str).str.strip() if b_kind else "Genel"
    books["_continent"] = books[b_cont].astype(str).str.strip() if b_cont else ""
    books["_mix"] = books[b_mix].astype(str).str.strip() if b_mix else ""
    books["_route"] = books[b_route].astype(str).str.strip() if b_route else ""
    books["_emoji"] = books[b_emoji].astype(str).str.strip() if b_emoji else "📚"

    # Record columns
    r_no = first_existing(records, ["Ogrenci_No", "Öğrenci_No", "No", "Öğrenci"])
    r_book = first_existing(records, ["Okudugu_Kitap", "Okuduğu_Kitap", "Kitap", "Kitap_Adi"])
    r_date = first_existing(records, ["Tarih", "Okuma_Tarihi", "Bitirme_Tarihi"])

    if r_no is None or r_book is None:
        raise ValueError("Kayıtlar tablosunda Ogrenci_No ve Okudugu_Kitap sütunları gerekli.")
    records["_no"] = records[r_no].astype(str).str.strip()
    records["_book"] = records[r_book].astype(str).str.strip()
    records["_date"] = records[r_date].astype(str).str.strip() if r_date else ""
    if r_date:
        records["_date_sort"] = pd.to_datetime(records[r_date], errors="coerce")
    else:
        records["_date_sort"] = pd.NaT

    return students, books, records


def title_lookup(books: pd.DataFrame):
    return {str(x).strip(): x for x in books["_title"].dropna().tolist()}


def parse_book_metadata(row):
    raw = str(row.get("_mix", "")).strip()
    kind = str(row.get("_kind", "")).strip()
    cont = str(row.get("_continent", "")).strip()

    if raw:
        parts = re.split(r"\s*(?:/|\||—|–|-|•)\s*", raw)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            known_conts = {"avrupa", "asya", "afrika", "kuzey amerika", "güney amerika", "okyanusya", "antarktika"}
            for p in parts:
                if p.lower() in known_conts:
                    cont = p
                elif not kind or kind.lower() == "genel":
                    kind = p
    if not kind or kind.lower() == "nan":
        kind = "Genel"
    if not cont or cont.lower() == "nan":
        cont = "Avrupa"
    return kind, cont


COLORS = {
    "Macera": (222, 145, 77),
    "Gizem": (113, 122, 171),
    "Fantastik": (140, 105, 171),
    "Mizah": (221, 157, 78),
    "Bilim": (76, 144, 170),
    "Doğa": (103, 154, 105),
    "Tarih": (170, 125, 74),
    "Klasik": (180, 108, 120),
    "Genel": (128, 128, 128),
}
CONTINENT_STYLE = {
    "Avrupa": {"color": "#e39b60", "fill": "#efc79c", "emoji": "🧭", "label": "Macera Kıtası"},
    "Asya": {"color": "#618db1", "fill": "#bed7e4", "emoji": "🔬", "label": "Bilim & Keşif Kıtası"},
    "Afrika": {"color": "#6d9b69", "fill": "#bfd3a9", "emoji": "🌿", "label": "Doğa Kıtası"},
    "Kuzey Amerika": {"color": "#c27d8f", "fill": "#e8bdc8", "emoji": "😂", "label": "Mizah Kıtası"},
    "Güney Amerika": {"color": "#7d9d72", "fill": "#c6d6bd", "emoji": "🌎", "label": "Hikâye Kıtası"},
    "Okyanusya": {"color": "#7d87b4", "fill": "#c8cce2", "emoji": "✨", "label": "Hayal Kıtası"},
    "Antarktika": {"color": "#8ea7b4", "fill": "#d9e4e8", "emoji": "❄️", "label": "Buzlar Kıtası"},
}

# Broad decorative “reading realms” – deliberately translucent so the real basemap remains visible.
CONTINENT_POLYGONS = {
    "Kuzey Amerika": [[72,-168],[73,-65],[55,-52],[25,-55],[7,-80],[13,-120],[25,-132],[50,-168]],
    "Güney Amerika": [[13,-82],[12,-35],[-55,-58],[-54,-78],[-5,-80]],
    "Avrupa": [[72,-25],[70,45],[52,42],[38,35],[35,8],[41,-10],[54,-22]],
    "Afrika": [[37,-18],[37,51],[4,53],[-35,37],[-35,12],[5,-18]],
    "Asya": [[77,40],[72,150],[8,150],[6,103],[19,69],[30,45],[48,40]],
    "Okyanusya": [[-10,112],[-11,155],[-45,160],[-47,113],[-24,105]],
    "Antarktika": [[-63,-180],[-63,180],[-90,180],[-90,-180]],
}


def color_for_kind(kind):
    k = str(kind).lower()
    for key, rgb in COLORS.items():
        if key.lower() in k:
            return rgb
    return COLORS["Genel"]


def rgba_hex(rgb, alpha=0.24):
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
    stage = 0
    for threshold in [0, 500, 1000, 2000, 5000, 10000, 20000]:
        if km >= threshold:
            stage += 1
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
      <defs><filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity=".25"/></filter></defs>
      <g filter="url(#s)">{body}{wheel}<path d="M8 56h110" stroke="#8a714b" stroke-width="2" stroke-linecap="round" stroke-dasharray="4 5"/><circle cx="16" cy="56" r="3" fill="#d9a441"/></g>
      <text x="65" y="67" text-anchor="middle" font-family="Nunito" font-size="8" font-weight="800" fill="#5e5343">{stage_km:,}+</text>
    </svg>'''
    return svg, name


def html_caravan_icon(km, color):
    svg, _ = caravan_svg(km, color)
    return f'<div class="caravan-marker">{svg}</div>'


# ----------------------------
# ROUTES
# ----------------------------

def parse_route_override(raw):
    if not raw or str(raw).lower() == "nan":
        return []
    pts = []
    for chunk in str(raw).split(";"):
        chunk = chunk.strip()
        m = re.match(r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$", chunk)
        if m:
            pts.append([float(m.group(1)), float(m.group(2))])
    return pts


def smooth_curve(a, b, bends=18):
    """Soft curved discovery trail between two coordinates."""
    lat1, lon1 = a
    lat2, lon2 = b
    points = []
    dx = lon2 - lon1
    dy = lat2 - lat1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    bend = min(9.0, max(1.3, length * 0.08))
    c1 = ((lat1 + lat2) / 2 + ny * bend, (lon1 + lon2) / 2 + nx * bend)
    for t in np.linspace(0, 1, bends):
        # quadratic Bezier
        lat = (1-t)**2 * lat1 + 2*(1-t)*t*c1[0] + t**2 * lat2
        lon = (1-t)**2 * lon1 + 2*(1-t)*t*c1[1] + t**2 * lon2
        points.append([lat, lon])
    return points


def path_between(a, b):
    # Within the same broad landmass: smooth trail. Between landmasses: curved “air/sea” leg.
    ca = continent_guess(*a)
    cb = continent_guess(*b)
    pts = smooth_curve(a, b, bends=24)
    return pts, (ca == cb)


def continent_guess(lat, lon):
    # Approximate only for styling; actual map geography comes from basemap.
    if lat < -10 and -85 < lon < -30:
        return "Güney Amerika"
    if lat < -10 and 110 < lon < 180:
        return "Okyanusya"
    if lat < -10 and -25 < lon < 55:
        return "Afrika"
    if lat > 35 and -15 < lon < 50:
        return "Avrupa"
    if lon < -35 and lat > 5:
        return "Kuzey Amerika"
    if lon < -30 and lat <= 5:
        return "Güney Amerika"
    if lon >= 50 or (lon >= 35 and lat > 0):
        return "Asya"
    return "Avrupa"


# ----------------------------
# MAP JS/CSS
# ----------------------------

def install_map_behaviour(m):
    map_name = m.get_name()
    css = f"""
    <style>
      #{map_name} .leaflet-tile-pane {{ filter: saturate(.72) sepia(.10) contrast(.98) brightness(1.04); }}
      #{map_name} .book-label {{
        transition: opacity .18s ease, transform .18s ease, font-size .18s ease;
        transform-origin: center center;
        pointer-events:auto;
      }}
      #{map_name}.zoom-calm .book-label {{ font-size: 9px !important; opacity:.62; padding:1px 3px !important; border-width:1px !important; box-shadow:none !important; }}
      #{map_name}.zoom-medium .book-label {{ font-size: 11px !important; opacity:.84; }}
      #{map_name}.zoom-close .book-label {{ font-size: 14px !important; opacity:1; }}
      #{map_name} .leaflet-control-zoom a {{ border-color:#d5c39c; color:#5c513f; background:#fffaf0; }}
      #{map_name} .leaflet-control-layers {{ border:1px solid #dac79e; background:#fffaf0; color:#443d33; }}
      .caravan-marker svg {{ display:block; }}
    </style>
    <script>
    (function() {{
      const map = {map_name};
      function updateBookLabels() {{
        const z = map.getZoom();
        map.getContainer().classList.remove('zoom-calm','zoom-medium','zoom-close');
        if (z < 3) map.getContainer().classList.add('zoom-calm');
        else if (z < 4.5) map.getContainer().classList.add('zoom-medium');
        else map.getContainer().classList.add('zoom-close');
      }}
      map.on('zoomend', updateBookLabels);
      setTimeout(updateBookLabels, 250);
    }})();
    </script>
    """
    m.get_root().html.add_child(Element(css))


# ----------------------------
# APP DATA
# ----------------------------
try:
    students, books, records = load_data()
    data_error = None
except Exception as exc:
    students, books, records = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    data_error = str(exc)

# Sidebar
st.sidebar.markdown("# 🧭 Gezgin Karavanlar")
st.sidebar.caption("4. Sınıf Okuma Macerası")
page = st.sidebar.radio(
    "Menü",
    ["🌍 Dünya Haritası", "🎒 Kaşiflerim", "📚 Kitaplık", "📊 Sınıf Günlüğü"],
)
st.sidebar.divider()
if st.sidebar.button("🔄 Verileri yenile", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
st.sidebar.info("Her kitap kaydı eklendiğinde rota, kilometre, unvan ve karavan seviyesi otomatik güncellenir.")

if data_error:
    st.error(f"Veriler okunamadı: {data_error}")
    st.stop()

# Derived book mapping
book_map = {str(r["_title"]): r for _, r in books.iterrows()}

records = records.copy()
records = records[records["_book"].isin(book_map.keys())].copy()
records = records.merge(
    books[["_title", "_lat", "_lon", "_km", "_kind", "_continent", "_mix", "_route", "_emoji"]],
    left_on="_book", right_on="_title", how="left"
)
if not records["_date_sort"].isna().all():
    records = records.sort_values(["_no", "_date_sort", "_book"], na_position="last")
else:
    records = records.sort_values(["_no", "_book"])

student_totals = records.groupby("_no")["_km"].sum().to_dict()
students["_km"] = students["_no"].map(student_totals).fillna(0)
students["_book_count"] = students["_no"].map(records["_no"].value_counts()).fillna(0).astype(int)

# Class totals
class_km = int(records["_km"].sum()) if not records.empty else 0
class_books = int(len(records))

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">4. SINIF · 2026–2027</div>
      <h1>📚 Kitaplarla Dünyayı Keşfediyoruz</h1>
      <p>Her kitap bir durak. Her sayfa bir yolculuk. Her çocuk kendi macerasının kaşifi. 🧭</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# HOME / MAP
# ----------------------------
if page == "🌍 Dünya Haritası":
    # Filters
    c1, c2, c3 = st.columns([1.1, 1.0, 1.2])
    with c1:
        students_options = ["Sınıfın tamamı"] + list(students["_no"].astype(str))
        selected_student = st.selectbox("👤 Kaşif", students_options)
    with c2:
        kind_options = ["Tüm türler"] + sorted([x for x in books["_kind"].dropna().unique() if str(x).strip()])
        selected_kind = st.selectbox("📖 Kitap türü", kind_options)
    with c3:
        title_options = ["Tüm kitaplar"] + sorted(books["_title"].dropna().astype(str).tolist())
        selected_title = st.selectbox("📍 Kitap / durak", title_options)

    filtered_books = books.copy()
    if selected_kind != "Tüm türler":
        filtered_books = filtered_books[filtered_books["_kind"] == selected_kind]
    if selected_title != "Tüm kitaplar":
        filtered_books = filtered_books[filtered_books["_title"] == selected_title]

    if selected_student != "Sınıfın tamamı":
        map_no = selected_student
        class_student_records = records[records["_no"] == map_no].copy()
    else:
        map_no = None
        class_student_records = records.copy()

    # Metrics
    total_km = int(students["_km"].sum())
    total_books = int(students["_book_count"].sum())
    all_world_goal = 40000
    goal_pct = min(100, int(total_km / all_world_goal * 100)) if all_world_goal else 0

    a,b,c,d = st.columns(4)
    for col, number, label in [
        (a, f"{total_km:,}", "🌍 sınıf kilometresi"),
        (b, f"{total_books}", "📚 kitap yolculuğu"),
        (c, f"{goal_pct}%", "🗺️ dünya turu"),
        (d, f"{len(students)}", "🧒 kaşif"),
    ]:
        with col:
            st.markdown(f'<div class="card metric-card"><div class="metric-number">{number}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🗺️ Masal Haritamız</div>', unsafe_allow_html=True)
    st.caption("Yakınlaşınca kitap isimleri büyür; uzaklaşınca sadeleşir. Karavanlar kilometre arttıkça aşama değiştirir.")

    m = folium.Map(location=[24, 15], zoom_start=2.35, min_zoom=1.7, max_zoom=7, tiles="CartoDB Voyager", control_scale=True)
    install_map_behaviour(m)

    # Continental reading realms
    realm_fg = folium.FeatureGroup(name="🌈 Kıta okuma bölgeleri", show=True)
    for cont, coords in CONTINENT_POLYGONS.items():
        style = CONTINENT_STYLE[cont]
        folium.Polygon(
            locations=coords,
            color=style["color"],
            weight=1.5,
            opacity=0.55,
            fill=True,
            fill_color=style["fill"],
            fill_opacity=0.22,
            tooltip=f"{style['emoji']} {cont}: {style['label']}",
        ).add_to(realm_fg)
    realm_fg.add_to(m)

    # Book destinations
    books_fg = folium.FeatureGroup(name="📚 Kitap durakları", show=True)
    for _, row in filtered_books.iterrows():
        if pd.isna(row["_lat"]) or pd.isna(row["_lon"]):
            continue
        kind, cont = parse_book_metadata(row)
        rgb = color_for_kind(kind)
        label_color = rgba_hex(rgb)
        short_title = str(row["_title"])
        label_html = f'''
          <div class="book-label" data-book-label="true" style="font-family:Nunito,sans-serif;font-weight:800;color:#31404b;background:rgba(255,250,240,.92);padding:3px 6px;border-radius:9px;border:2px solid {label_color};white-space:nowrap;text-align:center;box-shadow:0 3px 10px rgba(40,30,15,.15);">
             {str(row["_emoji"])} {short_title}
          </div>'''
        popup = folium.Popup(
            f"<div style='font-family:Nunito'><b>{short_title}</b><br>🌈 Tür: {kind}<br>🗺️ Kıta: {cont}<br>📄 Yolculuk: {int(row['_km'])} km</div>",
            max_width=280,
        )
        folium.Marker(
            [row["_lat"], row["_lon"]],
            icon=folium.DivIcon(html=label_html, class_name="book-marker"),
            popup=popup,
            tooltip=short_title,
        ).add_to(books_fg)
    books_fg.add_to(m)

    # Student trails
    if not class_student_records.empty:
        for student_no, group in class_student_records.groupby("_no"):
            student_row = students[students["_no"] == student_no].iloc[0]
            student_color = str(student_row["_color"]) or "Turuncu"
            color_map = {
                "Mavi":"#4f88bd","Turuncu":"#df8b43","Mor":"#8c72a8","Kırmızı":"#c85d63",
                "Yeşil":"#6d9b69","Sarı":"#d9a441","Pembe":"#cf7b98","Lacivert":"#4c638d",
                "Açık Mavi":"#6ea9c9","Açık Yeşil":"#7ba77b","Gri":"#7e858b","Siyah":"#40464e",
            }
            caravan_color = color_map.get(student_color.title(), "#df8b43")
            route_points = []
            ordered = group.dropna(subset=["_lat","_lon"]).copy()
            if not ordered.empty:
                previous = None
                for _, book_row in ordered.iterrows():
                    current = [float(book_row["_lat"]), float(book_row["_lon"])]
                    override = parse_route_override(book_row["_route"])
                    if previous is None:
                        route_points.extend(override if override else [current])
                    else:
                        if override:
                            route_points.extend(override)
                            route_points.append(current)
                        else:
                            segment, same_land = path_between(previous, current)
                            route_points.extend(segment)
                    previous = current

                if len(route_points) > 1:
                    # Main ribbon
                    folium.PolyLine(
                        route_points,
                        color=caravan_color,
                        weight=7 if selected_student != "Sınıfın tamamı" else 4,
                        opacity=0.18 if selected_student == "Sınıfın tamamı" else 0.24,
                        line_cap="round",
                    ).add_to(m)
                    folium.PolyLine(
                        route_points,
                        color=caravan_color,
                        weight=2.2 if selected_student != "Sınıfın tamamı" else 1.4,
                        opacity=0.80 if selected_student != "Sınıfın tamamı" else 0.38,
                        dash_array="2 10",
                        line_cap="round",
                    ).add_to(m)

                last = ordered.iloc[-1]
                last_pos = [float(last["_lat"]), float(last["_lon"])]
                km = float(student_row["_km"])
                title, _, role, remaining, _ = caravan_stage(km)
                icon_html = html_caravan_icon(km, caravan_color)
                popup = folium.Popup(
                    f"<div style='font-family:Nunito;min-width:200px'><b>🧭 {student_row['_name']}</b><br>🏆 {title}<br>🚐 {role}<br>🌍 {int(km):,} km<br>📚 {int(student_row['_book_count'])} kitap<br>📍 Son durak: {last['_title']}<br><small>Sonraki seviyeye: {int(remaining):,} km</small></div>",
                    max_width=300,
                )
                folium.Marker(
                    last_pos,
                    popup=popup,
                    tooltip=f"{student_row['_name']} · {int(km):,} km",
                    icon=folium.DivIcon(html=icon_html, class_name="caravan-marker", icon_size=(92,60), icon_anchor=(46,30)),
                ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    st_folium(m, width=None, height=690, returned_objects=[])

    # Goal card
    current_pct = min(100, class_km / 40000 * 100)
    st.markdown(
        f'''<div class="card" style="margin-top:16px"><div class="eyebrow">SINIF ORTAK HEDEFİ</div><div style="font-family:Baloo 2;font-size:26px;font-weight:800;color:#31404e">🌍 Dünyanın çevresinde bir tur</div><div class="progress-shell"><div class="progress-bar" style="width:{current_pct:.1f}%"></div></div><div style="display:flex;justify-content:space-between;margin-top:7px;color:#766b59;font-weight:800;font-size:13px"><span>{class_km:,} km</span><span>40.000 km</span></div></div>''',
        unsafe_allow_html=True,
    )

# ----------------------------
# STUDENTS
# ----------------------------
elif page == "🎒 Kaşiflerim":
    st.markdown('<div class="section-title">🎒 Kaşiflerim</div>', unsafe_allow_html=True)
    st.caption("Her öğrencinin toplam kilometresi arttıkça unvanı ve karavanı otomatik yükselir.")

    search = st.text_input("🔎 Öğrenci ara", placeholder="Ad veya öğrenci no")
    view_df = students.copy()
    if search.strip():
        q = search.strip().lower()
        view_df = view_df[view_df["_name"].str.lower().str.contains(q, na=False) | view_df["_no"].str.lower().str.contains(q, na=False)]

    cols = st.columns(3)
    for i, (_, row) in enumerate(view_df.sort_values("_km", ascending=False).iterrows()):
        with cols[i % 3]:
            km = float(row["_km"])
            name, emoji, role, remain, threshold = caravan_stage(km)
            pct = 100 if remain == 0 else min(100, max(0, (km-threshold) / max(1, (km-remain)-threshold) * 100))
            svg, _ = caravan_svg(km, "#" + "".join(f"{x:02x}" for x in COLORS.get(str(row["_color"]).strip().title(), COLORS["Genel"]))) if str(row["_color"]) in COLORS else caravan_svg(km, "#df8b43")
            st.markdown(
                f'''<div class="card" style="min-height:250px;margin-bottom:15px"><div style="display:flex;justify-content:space-between"><div><div class="eyebrow">KAŞİF #{row['_no']}</div><div style="font-family:Baloo 2;font-weight:800;font-size:24px;color:#2f3e4d">{row['_name']}</div></div><div style="font-size:28px">{emoji}</div></div><div style="margin:12px 0 2px">{svg}</div><div style="font-weight:800;color:#5a5147">🏆 {name}</div><div class="small-muted">{role} · {int(km):,} km · {int(row['_book_count'])} kitap</div><div class="progress-shell"><div class="progress-bar" style="width:{min(100,pct):.1f}%"></div></div><div class="small-muted" style="margin-top:5px">Sonraki seviyeye {int(remain):,} km</div></div>''',
                unsafe_allow_html=True,
            )

# ----------------------------
# LIBRARY
# ----------------------------
elif page == "📚 Kitaplık":
    st.markdown('<div class="section-title">📚 Dünya Okur Kütüphanesi</div>', unsafe_allow_html=True)
    st.caption("Kitapların konumu, türü ve kilometresi tek bir tablodan yönetilir. İsterseniz Google Sheet'e yeni sütunlar ekleyerek sistemi genişletebilirsiniz.")

    c1, c2 = st.columns(2)
    with c1:
        kind = st.selectbox("Tür", ["Tümü"] + sorted(books["_kind"].dropna().astype(str).unique().tolist()))
    with c2:
        cont = st.selectbox("Kıta", ["Tümü"] + sorted(books["_continent"].dropna().astype(str).unique().tolist()))
    lib = books.copy()
    if kind != "Tümü":
        lib = lib[lib["_kind"] == kind]
    if cont != "Tümü":
        lib = lib[lib["_continent"] == cont]

    read_counts = records["_book"].value_counts().to_dict()
    book_cols = st.columns(2)
    for i, (_, row) in enumerate(lib.sort_values("_title").iterrows()):
        kind_name, continent = parse_book_metadata(row)
        rgb = color_for_kind(kind_name)
        cover = '#%02x%02x%02x' % rgb
        count = int(read_counts.get(row["_title"], 0))
        with book_cols[i % 2]:
            st.markdown(
                f'''<div class="book-card"><div class="book-cover" style="background:{cover}">{row['_emoji']}</div><div><h4>{row['_title']}</h4><p>{kind_name} · {continent} · {int(row['_km'])} km</p><p>👣 {count} kaşif bu durağı ziyaret etti</p></div></div>''',
                unsafe_allow_html=True,
            )

# ----------------------------
# STATS
# ----------------------------
elif page == "📊 Sınıf Günlüğü":
    st.markdown('<div class="section-title">📊 Sınıf Okuma Günlüğü</div>', unsafe_allow_html=True)
    if records.empty:
        st.info("Henüz kayıt yok. İlk kitap kaydı eklendiğinde sınıf günlüğü burada oluşacak.")
        st.stop()

    # KPIs
    genre_counts = records["_kind"].replace("nan", "Genel").value_counts()
    popular_book = records["_book"].value_counts().index[0] if not records.empty else "—"
    top_student = students.sort_values("_km", ascending=False).iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    metrics = [
        (f"{class_km:,}", "🌍 toplam km"),
        (f"{class_books}", "📚 kitap yolculuğu"),
        (popular_book, "⭐ en çok keşfedilen kitap"),
        (f"{top_student['_name']}", "🧭 en ileri kaşif"),
    ]
    for col, (n,l) in zip([c1,c2,c3,c4], metrics):
        with col:
            st.markdown(f'<div class="card metric-card"><div class="metric-number" style="font-size:{25 if len(str(n))>16 else 34}px">{n}</div><div class="metric-label">{l}</div></div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown("#### 🌈 Türlere göre keşif")
        g = genre_counts.reset_index()
        g.columns = ["Tür", "Okunma"]
        fig = px.pie(g, values="Okunma", names="Tür", hole=.48)
        fig.update_layout(margin=dict(l=5,r=5,t=5,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### 🧭 Kaşif kilometreleri")
        rank = students[["_name","_km"]].sort_values("_km", ascending=True)
        fig2 = px.bar(rank, x="_km", y="_name", orientation="h")
        fig2.update_layout(margin=dict(l=10,r=10,t=5,b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="KM", yaxis_title=None)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 🏅 Kaşif rozetleri")
    badges = [
        ("📖", "İlk Kitap", int((students["_book_count"] >= 1).sum())),
        ("🧭", "500 KM Kaşifi", int((students["_km"] >= 500).sum())),
        ("🌍", "1.000 KM Gezgini", int((students["_km"] >= 1000).sum())),
        ("🚀", "5.000 KM Kıta Kaşifi", int((students["_km"] >= 5000).sum())),
        ("🌟", "10.000 KM Dünya Kaşifi", int((students["_km"] >= 10000).sum())),
    ]
    badge_cols = st.columns(len(badges))
    for col, (emo, label, count) in zip(badge_cols, badges):
        with col:
            st.markdown(f'<div class="badge"><div class="emoji">{emo}</div><b>{label}</b><span class="small-muted">{count} öğrenci</span></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">🧭 Gezgin Karavanlar · Okuma bir yarış değil, keşif yolculuğudur.</div>', unsafe_allow_html=True)
