import { siteConfig } from '../../site.config.mjs';

export { siteConfig };

export function withBase(path = '/') {
  const base = import.meta.env.BASE_URL;
  const cleanBase = base.endsWith('/') ? base.slice(0, -1) : base;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (cleanPath === '/') return `${cleanBase}/`;
  return `${cleanBase}${cleanPath}`.replace(/\/+/g, '/');
}

export function canonicalUrl(path = '/') {
  return new URL(withBase(path), import.meta.env.SITE).toString();
}
