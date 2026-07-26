import categories from '../data/categories.json';
import professions from '../data/professions.json';
import { basePath, siteUrl } from '../../site.config.mjs';

const escapeXml = (value: string) => value.replace(/[<>&'"]/g, (char) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[char] || char);

export function GET() {
  const base = basePath.endsWith('/') ? basePath.slice(0, -1) : basePath;
  const routes = [
    '/',
    '/metodoloji/',
    ...categories.map((category) => `/kategori/${category.slug}/`),
    ...professions.map((profession) => `/meslek/${profession.slug}/`),
  ];
  const urls = routes.map((route) => `<url><loc>${escapeXml(`${siteUrl}${base}${route}`)}</loc></url>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
