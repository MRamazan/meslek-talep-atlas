#!/usr/bin/env python3
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
categories = json.loads((root / 'src/data/categories.json').read_text(encoding='utf-8'))
professions = json.loads((root / 'src/data/professions.json').read_text(encoding='utf-8'))
audit = json.loads((root / 'src/data/data-audit.json').read_text(encoding='utf-8'))
reports = list((root / 'src/content/reports').glob('*.md'))

errors = []
if sum(c['jobCount'] for c in categories) != audit['totalJobs']:
    errors.append('Kategori ilan toplamı genel toplamla eşleşmiyor.')
if sum(p['count'] for p in professions) != audit['totalJobs']:
    errors.append('Meslek ilan toplamı genel toplamla eşleşmiyor.')
if len(categories) != audit['categoryCount']:
    errors.append('Kategori sayısı uyuşmuyor.')
if len(professions) != audit['professionCount']:
    errors.append('Meslek sayısı uyuşmuyor.')
if len(reports) != len(professions):
    errors.append('Rapor sayısı meslek sayısıyla eşleşmiyor.')

seen_ids = set()
seen_urls = set()
for profession in professions:
    if profession['count'] < audit['minimumProfessionJobs']:
        errors.append(f"Eşik altı meslek: {profession['name']}")
    if len(profession['sourceJobs']) != profession['count']:
        errors.append(f"Kaynak ilan sayısı uyuşmuyor: {profession['name']}")
    for job in profession['sourceJobs']:
        if job['jobId'] in seen_ids:
            errors.append(f"Tekrarlanan job_id: {job['jobId']}")
        if job['url'] in seen_urls:
            errors.append(f"Tekrarlanan URL: {job['url']}")
        seen_ids.add(job['jobId'])
        seen_urls.add(job['url'])

for path in reports:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'^wordCount:\s*(\d+)', text, re.M)
    if not match or not (450 <= int(match.group(1)) <= 700):
        errors.append(f"Rapor kelime sınırı dışında: {path.name}")
    for heading in [
        '## Kısa özet', '## Hızlı görünüm', '## İşverenlerin beklentileri',
        '## Teknik yetenekler ve araçlar', '## Deneyim, eğitim ve dil beklentileri',
        '## İşin gerçek sorumlulukları', '## Dikkat çeken pazar sinyalleri',
        '## Adaylar için çıkarım', '## Veri notu'
    ]:
        if heading not in text:
            errors.append(f"Eksik rapor bölümü ({heading}): {path.name}")

if len(seen_ids) != audit['uniqueJobIds']:
    errors.append('Benzersiz job_id sayısı denetim özetiyle eşleşmiyor.')
if len(seen_urls) != audit['uniqueUrls']:
    errors.append('Benzersiz URL sayısı denetim özetiyle eşleşmiyor.')

if errors:
    print('\n'.join(f'ERROR: {error}' for error in errors))
    raise SystemExit(1)
print(f"OK: {len(categories)} kategori, {len(professions)} meslek, {audit['totalJobs']} ilan, {len(reports)} rapor")
