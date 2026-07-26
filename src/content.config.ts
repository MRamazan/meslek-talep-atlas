import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const reports = defineCollection({
  loader: glob({ base: './src/content/reports', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    category: z.string(),
    categorySlug: z.string(),
    jobCount: z.number().int().min(8),
    description: z.string(),
    dataPeriod: z.string(),
    wordCount: z.number().int().min(450).max(700),
  }),
});

export const collections = { reports };
