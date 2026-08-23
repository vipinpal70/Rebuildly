import { promises as fs } from "fs";
import path from "path";
import { notFound } from "next/navigation";
import DynamicClientSite from "../../../components/DynamicClientSite";

/* Dynamic fallback for /sites/{slug} — reads public/previews/{slug}.json at
 * REQUEST time instead of via a build-time static import, so a newly generated
 * site is live immediately with zero rebuild. Next.js resolves a static folder
 * (app/sites/some-slug/page.tsx) in preference to this dynamic route whenever
 * both could match the same URL, so the existing per-lead static pages keep
 * working exactly as before — this route only ever serves slugs that don't
 * (yet) have one. A later `npm run build` naturally "promotes" any given site
 * to a prerendered static page without anything else changing. */

const SLUG_PATTERN = /^[a-z0-9-]+$/;

async function loadSiteConfig(slug: string): Promise<any | null> {
  if (!SLUG_PATTERN.test(slug)) return null; // guards against path traversal
  const filePath = path.join(process.cwd(), "public", "previews", `${slug}.json`);
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const siteConfig = await loadSiteConfig(slug);
  if (!siteConfig) return {};
  return {
    title: `${siteConfig.name || slug} | Custom Web Preview`,
    description: siteConfig.scraped_tagline || siteConfig.heroSubtitle || undefined,
  };
}

export default async function DynamicSitePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const siteConfig = await loadSiteConfig(slug);
  if (!siteConfig) notFound();
  return <DynamicClientSite siteConfig={siteConfig} />;
}
