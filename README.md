# 🧭 Gezgin Karavanlar — 4. Sınıf Okuma Macerası

Bu sürüm Streamlit + Folium + Google Sheets CSV ile çalışır.

## Yeni yapı
- Masalsı, sıcak renkli ana arayüz
- Dünya haritasında kıta bazlı “okuma bölgeleri”
- Kitap isimleri zoom seviyesine göre otomatik küçülür/büyür
- Her öğrencinin rotası ve son karavan konumu görünür
- Kilometre arttıkça karavan aşaması değişir
- Öğrenci, kitaplık ve sınıf istatistikleri ayrı sayfalarda
- Kitaplar için `Rota_Noktalari` alanı ile özel yol koridoru tanımlama desteği
- Mevcut sütun adlarının çoğu korunur; bazı yeni sütunlar isteğe bağlıdır

## Google Sheets sütunları
### Öğrenciler
Gerekli: `Ogrenci_No`
Önerilen: `Ad_Soyad`, `Karavan_Rengi`, `Harcanan_Mil`
İsteğe bağlı: `Karavan_Gorsel_URL`

### Kitaplar
Gerekli: `Kitap_Adi_Sehir`, `Enlem`, `Boylam`, `Sayfa_Sayisi_KM`
Önerilen: `Tur`, `Kita`
Mevcut yapı ile uyumlu: `Tur_Kita`
İsteğe bağlı: `Rota_Noktalari`, `Emoji`

`Rota_Noktalari` örneği:
`41.01,28.97; 41.35,29.15; 42.00,27.50; 43.20,20.00`

### Kayıtlar
Gerekli: `Ogrenci_No`, `Okudugu_Kitap`
Önerilen: `Tarih`

## Streamlit Cloud
1. `app.py`, `requirements.txt` ve `.streamlit/secrets.toml` dosyalarını repo'ya koy.
2. Gerçek URL'leri `secrets.toml` içindeki `[data]` alanına taşı.
3. `app.py` içindeki eski MapTiler anahtarını artık kullanma.
4. Main file olarak `app.py` seç.
