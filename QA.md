# Doğrulama kaydı

## Kaynak veri

- Filtre sonrası tekil ilan: 519
- Ana kategori: 17
- Alt meslek: 44
- Alt meslek ilan aralığı: 8-33
- Benzersiz `job_id`: 519
- Benzersiz URL: 519
- Ana kaynak: `site_icin_minimum_8_ilanli_meslekler.json`
- Kullanılabilir biçimler: JSON, JSONL, CSV, Excel ve TXT paket özeti

`python3 scripts/validate-data.py` ile kategori ve meslek toplamları, 8 ilan eşiği, ilan tekilliği, 44 Markdown raporu, gerekli rapor bölümleri ve 450-700 kelime sınırı denetlenir.

## Sayfa ve bağlantı doğrulaması

Doğrulama amaçlı statik çıktı `python3 scripts/fallback-build.py` ile aynı JSON ve Markdown içeriklerinden üretildi.

- HTML sayfası: 64
- Ana sayfa: 1
- Kategori sayfası: 17
- Meslek sayfası: 44
- Metodoloji: 1
- 404: 1
- Sitemap ve robots: mevcut
- Her HTML sayfasında tek H1: doğrulandı
- Title, description, canonical ve Open Graph alanları: doğrulandı
- `REPOSITORY_NAME` base yolu altındaki dahili hedefler: doğrulandı
- Eksik dahili hedef: 0

`node scripts/validate-build.mjs` bu kontrolleri tekrarlar.

## Görsel kontrol

Chromium tabanlı tarayıcıyla ana sayfa ve Veri Bilimi raporu 1440 px masaüstü ve 390 px mobil genişlikte render edildi. Dört görünümde de yatay taşma bulunmadı. Ekran görüntüleri `qa-screenshots/` klasöründedir.

## Ortam notu

Teslim ortamında npm paket deposu DNS erişimi kapalı olduğu için Astro paketi indirilemedi ve burada `astro build` çalıştırılamadı. Astro kaynak yapısı güncel resmi Content Collections, `site`/`base` ve statik çıktı API'lerine göre hazırlandı. GitHub Actions iş akışı bağımlılıkları yükleyip `npm run build` komutunu çalıştıracak biçimdedir. Çevrimdışı statik üretim, veri, SEO, sayfa, bağlantı ve responsive kontrolleri başarılıdır.
