# Meslek Talep Atlası

519 LinkedIn ilanından üretilmiş, 17 ana kategori ve 44 alt meslek için statik analiz sitesi. Astro ile build edilir ve GitHub Pages üzerinde sunucu gerektirmeden yayımlanır.

## Doğrulanan veri kapsamı

- 519 tekil ilan
- 17 ana kategori
- 44 alt meslek
- Her alt meslekte en az 8 ilan
- Ana kaynak: `site_icin_minimum_8_ilanli_meslekler.json`
- Raporlar: `src/content/reports/` altında 44 Markdown dosyası

Kaynak ZIP proje içine eklenmemiştir. Dönüştürülmüş, site için gerekli küçük JSON dosyaları `src/data/` altında bulunur.

## Yapılandırma

GitHub kullanıcı adı ve depo adı tek noktada tutulur:

```js
// site.config.mjs
export const siteConfig = {
  githubUsername: 'GITHUB_USERNAME',
  repositoryName: 'REPOSITORY_NAME',
  // ...
};
```

1. `GITHUB_USERNAME` değerini GitHub kullanıcı adınızla değiştirin.
2. `REPOSITORY_NAME` değerini oluşturacağınız depo adıyla değiştirin.
3. Kullanıcı sitesi (`kullaniciadi.github.io`) yayımlıyorsanız `basePath` değerini `/` olacak biçimde uyarlayın. Normal proje deposunda varsayılan `/<depo-adi>` yapısı doğrudur.

Tüm dahili bağlantılar `import.meta.env.BASE_URL` kullanan merkezi `withBase()` yardımcı fonksiyonundan geçer. Canonical, sitemap ve robots adresleri aynı yapılandırmayı kullanır.

## Yerel çalıştırma

Node.js 22 önerilir.

```bash
npm install --no-audit --no-fund
npm run check:data
npm run dev
```

Astro geliştirme sunucusu `base` yolu ile açılır. Terminalde gösterilen yerel adresi kullanın.

Üretim build'i ve dahili bağlantı kontrolü:

```bash
npm run build
npm run preview
```

`npm run build`, Astro build sonrasında `scripts/validate-build.mjs` dosyasını çalıştırır. Script ana sayfa, 17 kategori, 44 meslek, metodoloji ve 404 dahil toplam 64 HTML çıktısını; SEO alanlarını, tek H1 kullanımını, sitemap, robots ve base-path bağlantılarını denetler.

## Çevrimdışı doğrulama

Astro paket deposuna erişilemeyen ortamlarda, aynı JSON ve Markdown içeriklerinden doğrulama amaçlı statik çıktı üretilebilir:

```bash
npm run build:offline-check
```

Bu komut `dist/` altında 64 HTML sayfası üretir ve SEO, H1, dosya hedefleri ile `base` yolunu denetler. GitHub Pages dağıtımında asıl çıktı Astro ile `npm run build` komutundan üretilir.

## GitHub Pages yayımlama

1. GitHub'da `REPOSITORY_NAME` değerindeki adı taşıyan boş bir depo oluşturun.
2. `site.config.mjs` içindeki iki yer tutucuyu değiştirin.
3. Projeyi depoya gönderin:

```bash
git init
git add .
git commit -m "Meslek Talep Atlası ilk sürüm"
git branch -M main
git remote add origin https://github.com/GITHUB_USERNAME/REPOSITORY_NAME.git
git push -u origin main
```

4. GitHub deposunda **Settings > Pages** bölümüne gidin.
5. **Source** olarak **GitHub Actions** seçin.
6. `main` dalına yapılan push, `.github/workflows/deploy.yml` iş akışını başlatır.
7. Actions tamamlandığında site `https://GITHUB_USERNAME.github.io/REPOSITORY_NAME/` adresinde açılır.

## Proje yapısı

```text
src/
  components/          Tekrar kullanılabilir arayüz bileşenleri
  content/reports/     44 meslek analiz raporu
  data/                Kategori, meslek ve veri doğrulama JSON dosyaları
  layouts/             SEO ve sayfa kabuğu
  pages/               Ana sayfa, dinamik kategori/meslek, metodoloji, 404, sitemap, robots
  styles/              Global tasarım sistemi
scripts/                Veri, build ve çevrimdışı statik doğrulama araçları
.github/workflows/      GitHub Pages dağıtımı
site.config.mjs         Tek merkezi site/base yapılandırması
```

## Analiz yöntemi

- Kayıtlar `job_id` ve URL üzerinden tekilleştirildi.
- Meslek eşiği 8 ilandır.
- Beceri eş anlamlıları açık eşleşmelerde normalleştirildi.
- Oranlarda genel payda mesleğin toplam ilan sayısıdır.
- Deneyim, eğitim ve dil gibi eksik alanlarda yalnızca alanı dolu ilanlar payda olarak kullanılır.
- Tek dönemlik veriden yükseliş veya düşüş sonucu çıkarılmaz.
- Bu site resmi iş gücü istatistiği değildir.

Daha ayrıntılı açıklama sitedeki `/metodoloji/` sayfasındadır.
