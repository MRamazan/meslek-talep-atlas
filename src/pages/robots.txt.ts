import { basePath, siteUrl } from '../../site.config.mjs';

export function GET() {
  const base = basePath.endsWith('/') ? basePath.slice(0, -1) : basePath;
  const body = `User-agent: *
Allow: /
Sitemap: ${siteUrl}${base}/sitemap.xml
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
