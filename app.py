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

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=60) # 60 saniyede bir verileri günceller
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

# --- HESAPLAMA VE YARDIMCI FONKSİYONLAR ---
def unvan_ve_arac_belirle(km):
    if km < 100:
        return "İlk Adım Gezgini 🚶", "Vosvos (Küçük Araç)", "red", 100 - km
    elif km < 500:
        return "Meraklı Gezgin ⛺", "Çadırlı Karavan", "orange", 500 - km
    elif km < 1000:
        return "Deneyimli Gezgin 🚐", "Süslü Motokaravan", "blue", 1000 - km
    else:
        return "Usta Gezgin 🚀", "Dev Efsane Karavan", "purple", 0

# Öğrenci Bazlı KM ve Veri Birleştirme
if not df_kayit.empty and not df_kitap.empty:
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

    # Filtreleme Alanı
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

    # Harita Başlangıç Konumu
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="OpenStreetMap")

    # SENARYO 1: Özel Bir Öğrenci Seçildiyse (Rota ve Karavan İlerlemesi)
    if secilen_ogrenci != "Tüm Öğrenciler":
        ogrenci_no = int(secilen_ogrenci)
        ogrenci_kayitlari = df_birlesik[df_birlesik['Ogrenci_No'] == ogrenci_no]
        
        ogrenci_renk_row = df_ogrenci[df_ogrenci['Ogrenci_No'] == ogrenci_no]
        karavan_rengi = ogrenci_renk_row['Karavan_Rengi'].values[0] if not ogrenci_renk_row.empty else 'blue'

        toplam_km = ogrenci_kayitlari['Sayfa_Sayisi_KM'].sum()
        unvan, arac, simge_renk, _ = unvan_ve_arac_belirle(toplam_km)

        st.subheader(f"🚐 Öğrenci No: **{ogrenci_no}** | Unvan: **{unvan}** | Araç: **{arac}** | Toplam: **{toplam_km} KM**")

        if not ogrenci_kayitlari.empty:
            rota_koordinatlari = []
            
            for idx, row in ogrenci_kayitlari.iterrows():
                if pd.notnull(row['Enlem']) and pd.notnull(row['Boylam']):
                    koordinat = [row['Enlem'], row['Boylam']]
                    rota_koordinatlari.append(koordinat)
                    
                    folium.Marker(
                        location=koordinat,
                        popup=f"Kitap: {row['Kitap_Adi_Sehir']}<br>Tür: {row['Tur_Kita']}<br>KM: {row['Sayfa_Sayisi_KM']}",
                        tooltip=f"{row['Kitap_Adi_Sehir']}",
                        icon=folium.Icon(color="green", icon="book", prefix="fa")
                    ).add_to(m)

            # Rota Çizgisi Çizme
            if len(rota_koordinatlari) > 1:
                folium.PolyLine(
                    rota_koordinatlari,
                    color="blue",
                    weight=3,
                    opacity=0.8,
                    tooltip=f"Öğrenci {ogrenci_no} Rotası"
                ).add_to(m)

            # Son Konuma Karavan İkonu Koyma
            son_konum = rota_koordinatlari[-1]
            folium.Marker(
                location=son_konum,
                popup=f"<b>Öğrenci {ogrenci_no} Mevcut Konumu</b><br>Unvan: {unvan}",
                tooltip=f"Karavan No: {ogrenci_no} ({arac})",
                icon=folium.Icon(color=simge_renk, icon="car", prefix="fa")
            ).add_to(m)

    # SENARYO 2: Genel Görünüm (Filtrelere Göre)
    else:
        filtreli_kitaplar = df_kitap.copy()
        
        if secilen_kita != "Tüm Kıtalar / Türler":
            filtreli_kitaplar = filtreli_kitaplar[filtreli_kitaplar['Tur_Kita'] == secilen_kita]
        if secilen_kitap != "Tüm Kitaplar / Şehirler":
            filtreli_kitaplar = filtreli_kitaplar[filtreli_kitaplar['Kitap_Adi_Sehir'] == secilen_kitap]

        for idx, row in filtreli_kitaplar.iterrows():
            if pd.notnull(row['Enlem']) and pd.notnull(row['Boylam']):
                # Bu kitabı kimler okumuş bulalım
                okuyanlar = df_kayit[df_kayit['Okudugu_Kitap'] == row['Kitap_Adi_Sehir']]['Ogrenci_No'].tolist()
                okuyanlar_str = ", ".join(map(str, okuyanlar)) if okuyanlar else "Henüz kimse ziyaret etmedi."

                popup_icerik = f"""
                <b>Şehir/Kitap:</b> {row['Kitap_Adi_Sehir']}<br>
                <b>Kıta/Tür:</b> {row['Tur_Kita']}<br>
                <b>KM Değeri:</b> {row['Sayfa_Sayisi_KM']} KM<br>
                <b>Ziyaret Eden Gezginler (Öğrenci No):</b> {okuyanlar_str}
                """
                
                folium.Marker(
                    location=[row['Enlem'], row['Boylam']],
                    popup=folium.Popup(popup_icerik, max_width=300),
                    tooltip=f"{row['Kitap_Adi_Sehir']} ({len(okuyanlar)} Gezgin)",
                    icon=folium.Icon(color="red" if okuyanlar else "gray", icon="location-dot", prefix="fa")
                ).add_to(m)

    # Haritayı Ekrana Bas
    st_folium(m, width=1200, height=600)

# ==========================================
# 2. SAYFA: GEZGİNLER KULÜBÜ (UNVANLAR & MİLLER)
# ==========================================
elif sayfa == "🏆 Gezginler Kulübü":
    st.title("🏆 Gezginler Kulübü ve Seviye Tablosu")
    st.markdown("Öğrencilerimizin toplam katettiği kilometreler, unvanları ve uçak bileti alabilecekleri kullanılabilir milleri aşağıdadır.")

    # Öğrenci Bazlı KM Hesaplama
    if not df_birlesik.empty:
        ogrenci_km = df_birlesik.groupby('Ogrenci_No')['Sayfa_Sayisi_KM'].sum().reset_index()
    else:
        ogrenci_km = pd.DataFrame(columns=['Ogrenci_No', 'Sayfa_Sayisi_KM'])

    # Tüm öğrenciler listesiyle birleştirme (Okuma yapmayanlar da görünsün)
    kulup_df = pd.merge(df_ogrenci[['Ogrenci_No', 'Harcanan_Mil']], ogrenci_km, on='Ogrenci_No', how='left')
    kulup_df['Sayfa_Sayisi_KM'] = kulup_df['Sayfa_Sayisi_KM'].fillna(0)

    # Unvan ve Mil Hesaplamaları
    unvanlar = []
    araclar = []
    kalan_kmler = []
    kalan_miller = []

    for idx, row in kulup_df.iterrows():
        km = row['Sayfa_Sayisi_KM']
        harcanan = row['Harcanan_Mil']
        unvan, arac, _, kalan = unvan_ve_arac_belirle(km)
        
        unvanlar.append(unvan)
        araclar.append(arac)
        kalan_kmler.append(kalan)
        kalan_miller.append(int(km - harcanan))

    kulup_df['Unvan'] = unvanlar
    kulup_df['Karavan Tipi'] = araclar
    kulup_df['Toplam KM'] = kulup_df['Sayfa_Sayisi_KM'].astype(int)
    kulup_df['Uçuşa Hazır Mil'] = kalan_miller
    kulup_df['Sonraki Seviyeye Kalan KM'] = kalan_kmler

    # KVKK: Sadece Ogrenci_No göster, isim sütununu temizle
    gosterilecek_df = kulup_df[['Ogrenci_No', 'Unvan', 'Karavan Tipi', 'Toplam KM', 'Uçuşa Hazır Mil', 'Sonraki Seviyeye Kalan KM']]
    gosterilecek_df = gosterilecek_df.sort_values(by='Toplam KM', ascending=False).reset_index(drop=True)

    # Tabloyu Renkli Göster
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

        # Üst Özet Kartları
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