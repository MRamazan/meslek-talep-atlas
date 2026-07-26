#!/usr/bin/env python3
"""Astro bağımlılıkları çevrimdışıysa aynı veri/içerikten doğrulama amaçlı statik çıktı üretir.
Asıl dağıtım `npm run build` ile Astro tarafından yapılır; bu script veri, HTML, SEO ve base-yolu doğrulamasına yardımcıdır.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASE = "/REPOSITORY_NAME"
SITE = "https://GITHUB_USERNAME.github.io"
NAME = "Meslek Talep Atlası"

categories = json.loads((ROOT / "src/data/categories.json").read_text(encoding="utf-8"))
professions = json.loads((ROOT / "src/data/professions.json").read_text(encoding="utf-8"))
audit = json.loads((ROOT / "src/data/data-audit.json").read_text(encoding="utf-8"))
profession_by_slug = {p["slug"]: p for p in professions}


def with_base(path: str = "/") -> str:
    path = "/" + path.lstrip("/")
    return f"{BASE}{path}".replace("//", "/")


def canonical(path: str = "/") -> str:
    return f"{SITE}{with_base(path)}"


def inline(text: str) -> str:
    text = html.escape(str(text), quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def markdown_to_html(markdown: str) -> str:
    lines = markdown.strip().splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline(' '.join(x.strip() for x in paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph(); close_list(); continue
        if stripped.startswith("## "):
            flush_paragraph(); close_list()
            title = stripped[3:].strip()
            hid = re.sub(r"[^a-z0-9]+", "-", title.lower().translate(str.maketrans("çğıöşü", "cgiosu"))).strip("-")
            out.append(f'<h2 id="{html.escape(hid)}">{inline(title)}</h2>')
        elif stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(stripped[2:])}</li>")
        else:
            close_list(); paragraph.append(stripped)
    flush_paragraph(); close_list()
    return "\n".join(out)


def parse_report(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    data: dict[str, object] = {}
    for line in front.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"')
        elif re.fullmatch(r"\d+", value):
            value = int(value)
        data[key.strip()] = value
    return data, body.strip()


def stat(value, label):
    return f'<div class="stat"><strong class="stat-value">{html.escape(str(value))}</strong><span class="stat-label">{html.escape(label)}</span></div>'


def breadcrumbs(items):
    lis = []
    for i, (label, href) in enumerate(items):
        current = ' aria-current="page"' if i == len(items)-1 else ""
        content = f'<a href="{href}">{html.escape(label)}</a>' if href else f"<span>{html.escape(label)}</span>"
        lis.append(f"<li{current}>{content}</li>")
    return f'<nav class="breadcrumbs" aria-label="İçerik yolu"><div class="container"><ol>{"".join(lis)}</ol></div></nav>'


def layout(title: str, description: str, path: str, content: str, page_type: str = "website", scripts: str = "") -> str:
    full_title = title if title == NAME else f"{title} | {NAME}"
    can = canonical(path)
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<meta name="generator" content="Meslek Talep Atlası static verification renderer">
<meta name="description" content="{html.escape(description, quote=True)}"><meta name="theme-color" content="#ffffff">
<link rel="icon" type="image/svg+xml" href="{with_base('/favicon.svg')}">
<link rel="stylesheet" href="{with_base('/_astro/site.css')}">
<link rel="canonical" href="{can}">
<meta property="og:locale" content="tr_TR"><meta property="og:site_name" content="{NAME}"><meta property="og:type" content="{page_type}">
<meta property="og:title" content="{html.escape(full_title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{can}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{html.escape(full_title, quote=True)}"><meta name="twitter:description" content="{html.escape(description, quote=True)}">
<title>{html.escape(full_title)}</title>
</head>
<body><a class="skip-link" href="#main-content">İçeriğe geç</a>
<header class="site-header"><div class="container header-inner"><a class="brand" href="{with_base('/')}">{NAME}</a><nav class="nav" aria-label="Ana gezinme"><a href="{with_base('/')}">Kategoriler</a><a href="{with_base('/metodoloji/')}">Metodoloji</a></nav></div></header>
<main id="main-content" class="site-main">{content}</main>
<footer class="site-footer"><div class="container footer-inner"><p>LinkedIn ilanlarından türetilmiş bağımsız bir analiz çalışmasıdır; resmi iş gücü istatistiği değildir.</p><p><a href="{with_base('/metodoloji/')}">Veri ve metodoloji</a></p></div></footer>
{scripts}</body></html>'''


def write_page(rel: str, source: str) -> None:
    path = DIST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def category_card(c):
    top = "".join(f"<li>{html.escape(p['name'])} ({p['count']})</li>" for p in c["topProfessions"])
    search = " ".join([c["name"]] + [p["name"] for p in c["topProfessions"]]).lower()
    return f'''<article class="card category-card" data-filter-item data-search="{html.escape(search, quote=True)}"><div class="card-title"><h3><a href="{with_base('/kategori/'+c['slug']+'/')}">{html.escape(c['name'])}</a></h3><span class="badge">{c['jobCount']} ilan</span></div><div class="card-meta"><span>{c['professionCount']} meslek</span></div><ul class="card-list">{top}</ul></article>'''


def profession_card(p):
    skills = p.get("topSkills", [])[:5]
    skill_html = "".join(f"<span>{html.escape(s['name'])}</span>" for s in skills)
    search = f"{p['name']} {' '.join(s['name'] for s in skills)} {p['summary']}".lower()
    return f'''<article class="card profession-card" data-filter-item data-search="{html.escape(search, quote=True)}"><div class="card-title"><h3><a href="{with_base('/meslek/'+p['slug']+'/')}">{html.escape(p['name'])}</a></h3><span class="badge">{p['count']} ilan</span></div><p class="muted">{html.escape(p['summary'])}</p><div class="card-meta">{skill_html}</div></article>'''

FILTER_SCRIPT = '''<script>(()=>{const input=document.querySelector('input[type="search"]');const items=[...document.querySelectorAll('[data-filter-item]')];const empty=document.querySelector('.empty-state');if(!input)return;const normalize=v=>v.toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');input.addEventListener('input',()=>{const q=normalize(input.value.trim());let visible=0;items.forEach(item=>{const match=!q||normalize(item.dataset.search||'').includes(q);item.hidden=!match;if(match)visible++});if(empty)empty.hidden=visible!==0})})();</script>'''


def build_home():
    cards = "".join(category_card(c) for c in categories)
    content = f'''<section class="hero"><div class="container hero-grid"><div><p class="eyebrow">İş ilanı verisiyle meslek analizi</p><h1>Meslek talebini ilanların gerçek içeriğinden okuyun.</h1><p class="lead">Ana kategoriden mesleğe ilerleyin; teknik becerileri, birlikte istenen yetkinlikleri, sorumlulukları ve giriş bariyerlerini karşılaştırın.</p><div class="search-panel"><label class="search-label" for="site-search">Kategori veya meslek ara</label><input class="search-input" id="site-search" type="search" placeholder="Örnek: veri bilimi, Java, siber güvenlik" autocomplete="off" aria-describedby="site-search-help"><p class="search-help" id="site-search-help">Arama kategori adlarını, meslekleri ve öne çıkan becerileri tarar.</p></div></div><aside class="hero-note"><p><strong>Veri kapsamı</strong></p><p>Kaynak pakette kesin toplama tarihi verilmemiştir. İlanlar tek dönemlik bir örneklem olarak değerlendirilir; zaman serisi yorumu yapılmaz.</p><a href="{with_base('/metodoloji/')}">Yöntemi ve sınırlamaları inceleyin</a></aside></div></section>
<section class="section compact"><div class="container stats">{stat(audit['totalJobs'],'tekil ilan')}{stat(audit['categoryCount'],'ana kategori')}{stat(audit['professionCount'],'alt meslek')}{stat('8+','meslek başına ilan')}</div></section>
<section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow">Kategoriler</p><h2>17 ana kategori</h2></div><p>Toplam {audit['totalJobs']} ilan</p></div><div class="grid categories" id="category-grid">{cards}</div><div class="empty-state" hidden><p>Aramanızla eşleşen içerik bulunamadı.</p></div></div></section>'''
    write_page("index.html", layout(NAME, "519 LinkedIn ilanından üretilmiş 17 kategori ve 44 meslek için işveren beklentisi analizleri.", "/", content, scripts=FILTER_SCRIPT))


def build_categories():
    for c in categories:
        cps = sorted([p for p in professions if p["categorySlug"] == c["slug"]], key=lambda p: -p["count"])
        cards = "".join(profession_card(p) for p in cps)
        stats = stat(c["jobCount"], "ilan") + stat(c["professionCount"], "alt meslek") + stat(min(p["count"] for p in cps), "en küçük örneklem") + stat(max(p["count"] for p in cps), "en büyük örneklem")
        content = breadcrumbs([("Ana sayfa", with_base("/")), (c["name"], None)]) + f'''<header class="page-head"><div class="container"><p class="eyebrow">Ana kategori</p><h1>{html.escape(c['name'])}</h1><p class="lead">{html.escape(c['description'])}</p></div></header><section class="section compact"><div class="container stats">{stats}</div></section><section class="section"><div class="container"><div class="search-panel"><label class="search-label" for="profession-filter">Meslekleri filtrele</label><input class="search-input" id="profession-filter" type="search" placeholder="Meslek adı veya beceri yazın" autocomplete="off"><p class="search-help">Filtre, bu kategorideki meslek adlarını, kısa özetleri ve öne çıkan becerileri tarar.</p></div><div class="grid professions" style="margin-top:1rem">{cards}</div><div class="empty-state" hidden><p>Bu kategori içinde aramanızla eşleşen meslek bulunamadı.</p></div></div></section>'''
        desc = f"{c['name']} kategorisindeki {c['professionCount']} meslek ve {c['jobCount']} ilana dayalı talep analizi."
        write_page(f"kategori/{c['slug']}/index.html", layout(c["name"], desc, f"/kategori/{c['slug']}/", content, scripts=FILTER_SCRIPT))


def build_professions():
    for report_path in sorted((ROOT / "src/content/reports").glob("*.md")):
        fm, body = parse_report(report_path)
        p = profession_by_slug[str(fm["slug"])]
        skills = p.get("topSkills", [])[:8]
        skill_html = "".join(f'<li class="badge">{html.escape(s["name"])} · {s["count"]}</li>' for s in skills) or '<p class="muted">Yapılandırılmış beceri alanında yeterli veri yok.</p>'
        related_html = "".join(f'<li><a href="{with_base("/meslek/"+r["slug"]+"/")}">{html.escape(r["name"])}</a><span class="related-meta">{html.escape(r["category"])} · {r["count"]} ilan</span></li>' for r in p.get("related", []))
        sources_html = "".join(f'<li><div><a class="source-title" href="{html.escape(s["url"], quote=True)}" target="_blank" rel="noreferrer">{html.escape(s["title"])}</a><div class="source-meta">{html.escape(s["company"])} · {html.escape(s["location"])}</div></div><span class="badge">#{html.escape(str(s["jobId"]))}</span></li>' for s in p.get("sourceJobs", []))
        content = breadcrumbs([("Ana sayfa", with_base("/")), (str(fm["category"]), with_base("/kategori/"+str(fm["categorySlug"])+"/")), (str(fm["title"]), None)])
        content += f'''<header class="page-head"><div class="container"><p class="eyebrow">Meslek analizi</p><h1>{html.escape(str(fm['title']))}</h1><p class="lead">{html.escape(str(fm['description']))}</p></div></header><section class="section compact"><div class="container stats">{stat(fm['jobCount'],'incelenen ilan')}{stat(len(p.get('companies', [])),'öne çıkan şirket')}{stat(len(p.get('topSkills', [])),'raporlanan beceri')}{stat(fm['wordCount'],'analiz kelimesi')}</div></section><section class="section"><div class="container content-layout"><article class="prose reading">{markdown_to_html(body)}</article><aside class="sidebar"><div class="sidebar-block"><h2 class="sidebar-title">Öne çıkan beceriler</h2><ul class="skill-list">{skill_html}</ul></div><div class="sidebar-block"><h2 class="sidebar-title">İlgili meslekler</h2><ul class="related-list">{related_html}</ul></div><div class="sidebar-block"><h2 class="sidebar-title">Veri dönemi</h2><p class="muted">{html.escape(str(fm['dataPeriod']))}</p></div></aside></div></section>'''
        if sources_html:
            content += f'''<section class="section compact"><div class="container reading"><p class="eyebrow">Kaynak ilanlar</p><h2>İncelenen ilan bağlantıları</h2><p class="muted">Bağlantılar kaynak pakette URL bulunan ilanlara aittir ve zamanla erişilemez hale gelebilir.</p><ul class="source-list">{sources_html}</ul></div></section>'''
        write_page(f"meslek/{p['slug']}/index.html", layout(str(fm["title"]), str(fm["description"]), f"/meslek/{p['slug']}/", content, "article"))


def build_methodology():
    rows = "".join(f"<tr><td><code>{html.escape(str(f['name']))}</code></td><td>{html.escape(str(f['format']))}</td><td>{'-' if f['records'] is None else f['records']}</td><td>{html.escape(str(f['role']))}</td></tr>" for f in audit["availableFiles"])
    content = breadcrumbs([("Ana sayfa", with_base("/")), ("Metodoloji ve veri", None)]) + f'''<header class="page-head"><div class="container reading"><p class="eyebrow">Yöntem</p><h1>Metodoloji ve veri hakkında</h1><p class="lead">Bu sayfa, raporların hangi veriyle ve hangi hesaplama kurallarıyla üretildiğini açıklar.</p></div></header><section class="section compact"><div class="container reading prose">
<h2 id="veri-kaynagi">Veri kaynağı</h2><p>Ana kaynak, yüklenen paket içindeki <code>{audit['primarySource']}</code> dosyasıdır. Dosya ana kategori, alt meslek ve ilan kayıtlarını aynı hiyerarşide tutar; başlık, şirket, konum, açıklama, gereksinim, sorumluluk, beceri, deneyim, eğitim, dil, sektör ve kaynak URL alanlarını birlikte içerir.</p><p>Paket filtre öncesi 809 ilanı özetler. Bunların 804'ü sınıflandırılmış, 5'i veri eksiği olarak işaretlenmiştir. En az 8 ilan eşiğini geçmeyen 55 alt meslek ve 290 ilan çıkarıldıktan sonra sitede 519 ilan, 44 alt meslek ve 17 ana kategori kalmıştır.</p>
<h2 id="donem">Kapsanan dönem</h2><p>Kaynak pakette kesin toplama tarihi bulunmuyor. İlanlarda saat, gün ve hafta cinsinden göreli LinkedIn yayın etiketleri var. Bu nedenle analizler tek bir toplama dönemi olarak sunulur; belirli takvim tarihleri veya zaman içindeki artış ve azalış iddiaları üretilmez.</p>
<h2 id="tekillestirme">Tekilleştirme ve sınıflandırma</h2><p>Kayıtlar önce <code>job_id</code>, ardından URL üzerinden kontrol edildi. Sitedeki 519 kaydın 519 benzersiz iş ilanı kimliği ve 519 benzersiz URL'si vardır. Kategori ve alt meslek etiketleri kaynak dosyadan alınmıştır; sitede yeni ilan veya sınıflandırma üretilmemiştir.</p><p>Beceri adlarında yalnızca açık eş anlamlılar normalleştirildi: örneğin JS ile JavaScript, AWS ile Amazon Web Services, GCP ile Google Cloud ve Dotnet ile .NET aynı başlık altında toplandı. Farklı teknolojiler benzer amaç taşıdıkları için birleştirilmedi. R&amp;D metinlerinden yanlışlıkla türeyebilen tek harfli R etiketi, açık R programlama bağlamı yoksa çıkarıldı.</p>
<h2 id="oranlar">Oranlar nasıl hesaplandı?</h2><p>Genel beceri, tema, kariyer seviyesi, şirket ve konum oranlarında payda ilgili meslekteki tüm ilanlardır. Deneyim, eğitim ve dil gibi eksik olabilen alanlarda gerçek payda ayrıca belirtilir. Örneğin deneyim yılı yalnızca 10 ilanda varsa medyan ve ortalama bu 10 ilan üzerinden hesaplanır.</p><p>Görev temaları açıklama, gereksinim ve sorumluluk metinlerindeki anahtar kavramların ilan düzeyinde varlığıyla sayılmıştır. Aynı tema bir ilanda birçok kez geçse bile o ilan için bir kez sayılır. Birlikte talep edilen beceri paketleri, aynı ilanda yer alan normalize edilmiş beceri çiftlerinden üretilir.</p>
<h2 id="sinirlamalar">Örneklem sınırlamaları</h2><div class="notice"><strong>Bu çalışma resmi iş gücü istatistiği değildir.</strong> LinkedIn'de görünen, pakete alınan ve en az 8 ilan eşiğini geçen mesleklerden oluşan bir örneklemdir.</div><p>İlan metinleri şirketlerin yazım tercihlerini, tekrarlarını ve eksik alanlarını taşır. Belirtilmeyen bir beceri veya eğitim düzeyi, aranmadığı anlamına gelmez. Başvuru sayısı etiketleri gerçek aday kalitesini, işe alınma olasılığını veya tamamlanmış başvuru sayısını ölçmez. Küçük alt gruplarda tek bir şirket veya sektör genel görünümü etkileyebilir.</p>
<h2 id="dosyalar">Dosya envanteri</h2><div class="table-wrap"><table><thead><tr><th>Dosya</th><th>Biçim</th><th>Kayıt</th><th>Kullanım</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>'''
    write_page("metodoloji/index.html", layout("Metodoloji ve veri", "Meslek Talep Atlası veri kaynağı, tekilleştirme, sınıflandırma, oran hesaplama ve örneklem sınırlamaları.", "/metodoloji/", content))


def build_404():
    content = f'<section class="section"><div class="container reading"><p class="eyebrow">404</p><h1>Sayfa bulunamadı.</h1><p class="lead">Bağlantı değişmiş veya adres hatalı olabilir.</p><p><a href="{with_base('/')}">Ana sayfadaki kategorilere dönün</a></p></div></section>'
    write_page("404.html", layout("Sayfa bulunamadı", "Aradığınız sayfa bulunamadı.", "/404/", content))


def build_static_assets():
    (DIST / "_astro").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "src/styles/global.css", DIST / "_astro/site.css")
    shutil.copy2(ROOT / "public/favicon.svg", DIST / "favicon.svg")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    urls = [canonical("/")] + [canonical(f"/kategori/{c['slug']}/") for c in categories] + [canonical(f"/meslek/{p['slug']}/") for p in professions] + [canonical("/metodoloji/")]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"  <url><loc>{html.escape(u)}</loc></url>" for u in urls) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: {BASE}/\nSitemap: {canonical('/sitemap.xml')}\n", encoding="utf-8")


def main():
    if DIST.exists(): shutil.rmtree(DIST)
    build_static_assets(); build_home(); build_categories(); build_professions(); build_methodology(); build_404()
    html_count = len(list(DIST.rglob("*.html")))
    print(json.dumps({"dist": str(DIST), "html_pages": html_count, "categories": len(categories), "professions": len(professions)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
