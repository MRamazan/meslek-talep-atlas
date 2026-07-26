#!/usr/bin/env python3
"""Yeni bir kaynak paketiyle içerik üretmek için başlangıç noktası.

Mevcut proje, yüklenen paketten önceden üretilmiş JSON ve Markdown içeriklerini içerir.
Bu script kaynak paketinin temel doğrulamasını yapar. Rapor üretim mantığı proje tesliminde
kullanılan veri dönüşümüyle aynı ilkeleri izlemelidir: job_id/URL tekilleştirme, 8 ilan eşiği,
beceri eş anlamlı normalizasyonu ve eksik alanlarda gerçek payda.
"""
import argparse
import json
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('zip_path', type=Path)
args = parser.parse_args()
with zipfile.ZipFile(args.zip_path) as archive:
    name = 'site_icin_minimum_8_ilanli_meslekler.json'
    if name not in archive.namelist():
        raise SystemExit(f'Eksik ana kaynak: {name}')
    data = json.loads(archive.read(name).decode('utf-8'))
jobs = [job for category in data['categories'] for profession in category['subprofessions'] for job in profession['jobs']]
ids = {str(job['job_id']) for job in jobs}
urls = {job['url'] for job in jobs if job.get('url')}
professions = [profession for category in data['categories'] for profession in category['subprofessions']]
assert len(ids) == len(jobs), 'job_id tekrarları var'
assert len(urls) == len(jobs), 'URL tekrarları veya eksikleri var'
assert all(len(p['jobs']) >= 8 for p in professions), '8 ilan eşiği sağlanmıyor'
print(f"Doğrulandı: {len(jobs)} ilan, {len(data['categories'])} kategori, {len(professions)} meslek")
print('Not: Teslim edilen içerikler zaten üretilmiştir. Yeni paket için rapor metinleri ve site JSON dosyaları yeniden oluşturulmalıdır.')
