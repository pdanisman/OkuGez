import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Gezgin Karavanlar Okuma Projesi",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GOOGLE SHEETS VERİ LİNKLERİ ---
OGRENCILER_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=0&single=true&output=csv"
KITAPLAR_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=1390307822&single=true&output=csv"
KAYITLAR_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjaErnK01S9u8xTncNbrOBKdqbvFdp90XlL8zTZddMjDWdFVbj130XnhmBuIbGSpX-jBXkpZ9FZ2tk/pub?gid=509265349&single=true&output=csv"

# --- RENK ÇEVİRİ SÖZLÜĞÜ ---
RENK_SOZLUGU = {
    "Mavi": "blue", "Turuncu": "orange", "Mor": "purple", 
    "Kırmızı": "red", "Yeşil": "green", "Sarı": "beige", 
    "Pembe": "pink", "Siyah": "black", "Gri": "gray",
    "Açık Mavi": "lightblue", "Lacivert": "darkblue",
    "Koyu Kırmızı": "darkred", "Açık Yeşil": "lightgreen"
}

def renk_cevir(turkce_renk):
    return RENK_SOZLUGU.get(str(turkce_renk).strip().title(), "blue")

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=60)
def verileri_yukle():
    try:
        df_ogrenci = pd.read_csv(OGRENCILER_URL)
        df_kitap = pd.read_csv(KITAPLAR_URL)
        df_kayit = pd.read_csv(KAYITLAR_URL)

        # Boşlukları temizleme
        df_ogrenci.columns = df_ogrenci.columns.str.strip()
        df_kitap.columns = df_kitap.columns.str.strip()
        df_kayit.columns = df_kayit.columns.str.strip()

        # Sayısal veri dönüşümleri
        df_kitap['Enlem'] = pd.to_numeric(df_kitap['Enlem'], errors='coerce')
        df_kitap['Boylam'] = pd.to_numeric(df_kitap['Boylam'], errors='coerce')
        df_kitap['Sayfa_Sayisi_KM'] = pd.to_numeric(df_kitap['Sayfa_Sayisi_KM'], errors='coerce').fillna(0)
        df_ogrenci['Harcanan_Mil'] = pd.to_numeric(df_ogrenci['Harcanan_Mil'], errors='coerce').fillna(0)
        
        # Metin temizleme
        df_kayit['Okudugu_Kitap'] = df_kayit['Okudugu_Kitap'].astype(str).str.strip()
        df_kitap['Kitap_Adi_Sehir'] = df_kitap['Kitap_Adi_Sehir'].astype(str).str.strip()

        return df_ogrenci, df_kitap, df_kayit
    except Exception as e:
        st.error(f"Veri yüklenirken hata oluştu: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_ogrenci, df_kitap, df_kayit = verileri_yukle()

# --- HESAPLAMA YARDIMCI FONKSİYONLARI ---
def unvan_ve_arac_belirle(km):
    if km < 100:
        return "İlk Adım Gezgini 🚶", "Vosvos", 100 - km
    elif km < 500:
        return "Meraklı Gezgin ⛺", "Çadırlı Karavan", 500 - km
    elif km < 1000:
        return "Deneyimli Gezgin 🚐", "Süslü Motokaravan", 1000 - km
    else:
        return "Usta Gezgin 🚀", "Dev Efsane Karavan", 0

if not df_kayit.empty and not df_kitap.empty:
    # Okuma sırasını korumak için inner join yapıyoruz
    df_birlesik = pd.merge(df_kayit, df_kitap, left_on='Okudugu_Kitap', right_on='Kitap_Adi_Sehir', how='inner')
else:
    df_birlesik = pd.DataFrame()

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.title("📌 Gezgin Menüsü")
sayfa = st.sidebar.radio("Gitmek İstediğiniz Sayfa:", ["🗺️ Dünya Haritası ve Keşifler", "🏆 Gezginler Kulübü", "📊 Seyahat İstatistikleri"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Bilgi:** Her cuma yeni kitap okundukça haritanız güncellenir.")

# ==========================================
# 1. SAYFA: DÜNYA HARİTASI VE KEŞİFLER
# ==========================================
if sayfa == "🗺️ Dünya Haritası ve Keşifler":
    st.title("🌍 Gezgin Karavanlar Dünya Haritası")
    st.markdown("Öğrencilerimizin okudukları kitaplarla dünya üzerinde katettiği rotaları buradan inceleyebilirsiniz.")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        ogrenci_listesi = ["Tüm Öğrenciler"] + sorted(list(df_ogrenci['Ogrenci_No'].astype(str).unique()))
        secilen_ogrenci = st.selectbox("👤 Öğrenci No Seçin:", ogrenci_listesi)
        
    with col2:
        kita_listesi = ["Tüm Kıtalar / Türler"] + sorted(list(df_kitap['Tur_Kita'].dropna().unique()))
        secilen_kita = st.selectbox("🗺️ Kıta / Tür Seçin:", kita_listesi)

    with col3:
        kitap_listesi = ["Tüm Kitaplar / Şehirler"] + sorted(list(df_kitap['Kitap_Adi_Sehir'].dropna().unique()))
        secilen_kitap = st.selectbox("📚 Kitap / Şehir Seçin:", kitap_listesi)

    # Harita Başlangıç Konumu (CartoDB Positron daha sade bir arka plan sunar, renkler daha net görünür)
    m = folium.Map(location=[25, 10], zoom_start=2, tiles="CartoDB positron")

    # Kıtaları Renklendirme (GeoJSON Kullanarak)
    KITALAR_GEOJSON_URL = "https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/f3fde312c9b8168af6254ce1410dd4dda4a31941/continents.json"
    
    def kita_stili(feature):
        kita_renkleri = {
            "Asia": "#ffb3ba", "Europe": "#baffc9", "Africa": "#ffdfba",
            "North America": "#bae1ff", "South America": "#ffffba", "Oceania": "#e8baff"
        }
        kita_adi = feature['properties'].get('CONTINENT', 'Unknown')
        return {
            'fillColor': kita_renkleri.get(kita_adi, '#ffffff'),
            'color': '#888888',
            'weight': 1,
            'fillOpacity': 0.35
        }

    try:
        folium.GeoJson(KITALAR_GEOJSON_URL, name="Kıtalar", style_function=kita_stili).add_to(m)
    except Exception:
        pass # Eğer github gist bağlantısı anlık koparsa harita çökmesin

    # Kitapları (Şehirleri) Metin Olarak Ekleme
    filtreli_kitaplar = df_kitap.copy()
    if secilen_kita != "Tüm Kıtalar / Türler":
        filtreli_kitaplar = filtreli_kitaplar[filtreli_kitaplar['Tur_Kita'] == secilen_kita]
    if secilen_kitap != "Tüm Kitaplar / Şehirler":
        filtreli_kitaplar = filtreli_kitaplar[filtreli_kitaplar['Kitap_Adi_Sehir'] == secilen_kitap]

    for idx, row in filtreli_kitaplar.iterrows():
        if pd.notnull(row['Enlem']) and pd.notnull(row['Boylam']):
            folium.Marker(
                location=[row['Enlem'], row['Boylam']],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        font-family: 'Comic Sans MS', cursive, sans-serif; 
                        font-size: 12px; 
                        font-weight: bold; 
                        color: #2c3e50; 
                        background-color: rgba(255, 255, 255, 0.85); 
                        padding: 3px 6px; 
                        border-radius: 8px;
                        border: 2px solid #34495e;
                        white-space: nowrap;
                        text-align: center;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                        ">{row['Kitap_Adi_Sehir']}</div>"""
                )
            ).add_to(m)

    # --- ROTA VE KARAVAN GÖSTERİMİ ---
    if not df_birlesik.empty:
        # Hangi öğrencilerin çizileceğini belirle
        gosterilecek_ogrenciler = [int(secilen_ogrenci)] if secilen_ogrenci != "Tüm Öğrenciler" else df_birlesik['Ogrenci_No'].unique()

        for ogrenci_no in gosterilecek_ogrenciler:
            ogrenci_kayitlari = df_birlesik[df_birlesik['Ogrenci_No'] == ogrenci_no]
            
            if not ogrenci_kayitlari.empty:
                # Öğrencinin karavan rengini Excel'den çekip İngilizceye çevir
                renk_satiri = df_ogrenci[df_ogrenci['Ogrenci_No'] == ogrenci_no]
                tr_renk = renk_satiri['Karavan_Rengi'].values[0] if not renk_satiri.empty else 'Mavi'
                karavan_rengi = renk_cevir(tr_renk)

                # Rota koordinatlarını topla
                rota_koordinatlari = []
                for idx, row in ogrenci_kayitlari.iterrows():
                    if pd.notnull(row['Enlem']) and pd.notnull(row['Boylam']):
                        rota_koordinatlari.append([row['Enlem'], row['Boylam']])

                # Çizgi çizimi (Sadece 1'den fazla kitap okuduysa rota çizilebilir)
                if len(rota_koordinatlari) > 1:
                    folium.PolyLine(
                        rota_koordinatlari,
                        color=karavan_rengi,
                        weight=3 if secilen_ogrenci != "Tüm Öğrenciler" else 2,
                        opacity=0.8 if secilen_ogrenci != "Tüm Öğrenciler" else 0.5, # Tüm öğrencilerdeyken çizgiler birbirine karışmasın diye şeffaflık artırıldı
                        dash_array='5, 5', # Kesik çizgilerle yol efekti
                        tooltip=f"Öğrenci {ogrenci_no} Rotası"
                    ).add_to(m)

                # Son kitaba karavan ikonu yerleştir
                if rota_koordinatlari:
                    son_konum = rota_koordinatlari[-1]
                    son_kitap = ogrenci_kayitlari.iloc[-1]
                    toplam_km = ogrenci_kayitlari['Sayfa_Sayisi_KM'].sum()
                    unvan, arac, _ = unvan_ve_arac_belirle(toplam_km)

                    # Öğrenci numarasını ve bilgilerini içeren Karavan İkonu
                    folium.Marker(
                        location=son_konum,
                        popup=f"<b>Öğrenci No:</b> {ogrenci_no}<br><b>Unvan:</b> {unvan}<br><b>Araç:</b> {arac}<br><b>Son Durak:</b> {son_kitap['Kitap_Adi_Sehir']}<br><b>Toplam KM:</b> {toplam_km}",
                        tooltip=f"No: {ogrenci_no} ({tr_renk} Karavan)",
                        icon=folium.Icon(color=karavan_rengi, icon="caravan", prefix="fa")
                    ).add_to(m)

    st_folium(m, width=1200, height=650)

# ==========================================
# 2. SAYFA: GEZGİNLER KULÜBÜ (UNVANLAR & MİLLER)
# ==========================================
elif sayfa == "🏆 Gezginler Kulübü":
    st.title("🏆 Gezginler Kulübü ve Seviye Tablosu")
    st.markdown("Öğrencilerimizin toplam katettiği kilometreler, unvanları ve uçak bileti alabilecekleri kullanılabilir milleri aşağıdadır.")

    if not df_birlesik.empty:
        ogrenci_km = df_birlesik.groupby('Ogrenci_No')['Sayfa_Sayisi_KM'].sum().reset_index()
    else:
        ogrenci_km = pd.DataFrame(columns=['Ogrenci_No', 'Sayfa_Sayisi_KM'])

    kulup_df = pd.merge(df_ogrenci[['Ogrenci_No', 'Harcanan_Mil', 'Karavan_Rengi']], ogrenci_km, on='Ogrenci_No', how='left')
    kulup_df['Sayfa_Sayisi_KM'] = kulup_df['Sayfa_Sayisi_KM'].fillna(0)

    unvanlar, araclar, kalan_kmler, kalan_miller = [], [], [], []

    for idx, row in kulup_df.iterrows():
        km = row['Sayfa_Sayisi_KM']
        harcanan = row['Harcanan_Mil']
        unvan, arac, kalan = unvan_ve_arac_belirle(km)
        
        unvanlar.append(unvan)
        araclar.append(arac)
        kalan_kmler.append(kalan)
        kalan_miller.append(int(km - harcanan))

    kulup_df['Unvan'] = unvanlar
    kulup_df['Karavan Tipi'] = araclar
    kulup_df['Toplam KM'] = kulup_df['Sayfa_Sayisi_KM'].astype(int)
    kulup_df['Uçuşa Hazır Mil'] = kalan_miller
    kulup_df['Sonraki Seviyeye Kalan KM'] = kalan_kmler

    gosterilecek_df = kulup_df[['Ogrenci_No', 'Karavan_Rengi', 'Unvan', 'Karavan Tipi', 'Toplam KM', 'Uçuşa Hazır Mil', 'Sonraki Seviyeye Kalan KM']]
    gosterilecek_df = gosterilecek_df.sort_values(by='Toplam KM', ascending=False).reset_index(drop=True)

    st.dataframe(gosterilecek_df, use_container_width=True)

# ==========================================
# 3. SAYFA: SEYAHAT İSTATİSTİKLERİ
# ==========================================
elif sayfa == "📊 Seyahat İstatistikleri":
    st.title("📊 Sınıf Seyahat İstatistikleri")
    
    if not df_birlesik.empty:
        toplam_sinif_km = int(df_birlesik['Sayfa_Sayisi_KM'].sum())
        toplam_okunan_kitap = len(df_birlesik)
        en_populer_tur = df_birlesik['Tur_Kita'].mode()[0] if not df_birlesik['Tur_Kita'].empty else "Yok"

        col1, col2, col3 = st.columns(3)
        col1.metric("🌍 Sınıfça Katetimiz Yol", f"{toplam_sinif_km} KM")
        col2.metric("📚 Toplam Okunan Kitap", f"{toplam_okunan_kitap} Adet")
        col3.metric("🏆 En Çok Gezilen Kıta/Tür", f"{en_populer_tur}")

        st.markdown("---")

        col_grafik1, col_grafik2 = st.columns(2)

        with col_grafik1:
            st.subheader("Türlere / Kıtala Göre Okuma Dağılımı")
            tur_counts = df_birlesik['Tur_Kita'].value_counts().reset_index()
            tur_counts.columns = ['Tur_Kita', 'Okunma Sayısı']
            fig1 = px.pie(tur_counts, values='Okunma Sayısı', names='Tur_Kita', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig1, use_container_width=True)

        with col_grafik2:
            st.subheader("En Çok Ziyaret Edilen 5 Şehir / Kitap")
            kitap_counts = df_birlesik['Kitap_Adi_Sehir'].value_counts().head(5).reset_index()
            kitap_counts.columns = ['Kitap / Şehir', 'Ziyaret Sayısı']
            fig2 = px.bar(kitap_counts, x='Kitap / Şehir', y='Ziyaret Sayısı', color='Ziyaret Sayısı', color_continuous_scale='Viridis')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Henüz okuma kaydı bulunamadı. Cuma mülakatlarından sonra veriler burada görünecektir!")
