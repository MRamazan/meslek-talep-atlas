import { defineConfig } from 'astro/config';
import { basePath, siteUrl } from './site.config.mjs';

export default defineConfig({
  site: siteUrl,
  base: basePath,
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
