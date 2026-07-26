import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { basePath } from '../site.config.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const base = basePath.endsWith('/') ? basePath.slice(0, -1) : basePath;
const htmlFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.name.endsWith('.html')) htmlFiles.push(full);
  }
};
walk(dist);

const errors = [];
const hrefPattern = /(?:href|src)=["']([^"'#?]+)(?:[?#][^"']*)?["']/g;
for (const file of htmlFiles) {
  const source = fs.readFileSync(file, 'utf8');
  const h1Count = (source.match(/<h1(?:\s|>)/g) || []).length;
  if (h1Count !== 1) errors.push(`${path.relative(dist, file)}: H1 sayısı ${h1Count}`);
  for (const required of ['<title>', 'name="description"', 'rel="canonical"', 'property="og:title"']) {
    if (!source.includes(required)) errors.push(`${path.relative(dist, file)}: SEO alanı eksik ${required}`);
  }
  let match;
  while ((match = hrefPattern.exec(source))) {
    const url = match[1];
    if (/^(https?:|mailto:|tel:|data:)/.test(url)) continue;
    if (!url.startsWith(base + '/') && url !== base) {
      errors.push(`${path.relative(dist, file)}: base dışında bağlantı ${url}`);
      continue;
    }
    let rel = url.slice(base.length);
    if (!rel || rel === '/') rel = '/index.html';
    else if (rel.endsWith('/')) rel += 'index.html';
    const target = path.join(dist, rel.replace(/^\//, ''));
    if (!fs.existsSync(target)) errors.push(`${path.relative(dist, file)}: hedef bulunamadı ${url}`);
  }
}
const expectedHtml = 1 + 17 + 44 + 1 + 1;
if (htmlFiles.length !== expectedHtml) errors.push(`HTML sayısı ${htmlFiles.length}, beklenen ${expectedHtml}`);
for (const required of ['sitemap.xml', 'robots.txt', '404.html', 'favicon.svg']) {
  if (!fs.existsSync(path.join(dist, required))) errors.push(`Eksik çıktı: ${required}`);
}

const astroAssetsDir = path.join(dist, '_astro');
const hasCssAsset =
  fs.existsSync(astroAssetsDir) &&
  fs.readdirSync(astroAssetsDir, { withFileTypes: true }).some(
    (entry) => entry.isFile() && entry.name.endsWith('.css'),
  );

if (!hasCssAsset) errors.push('Eksik çıktı: _astro altında CSS dosyası bulunamadı');

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log(`OK: ${htmlFiles.length} HTML sayfası, SEO, H1, base-path ve dosya bağlantıları doğrulandı.`);
