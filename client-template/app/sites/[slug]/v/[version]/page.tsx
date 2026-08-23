import { promises as fs } from "fs";
import path from "path";
import { notFound } from "next/navigation";
import DynamicClientSite from "../../../../../components/DynamicClientSite";

/* Public, unauthenticated route for a single ARCHIVED version of a site — reads
 * public/previews/versions/{slug}/v{n}.json at REQUEST time (same technique as
 * the live /sites/[slug] fallback), so both the admin and the client can browse
 * any past design via a plain shareable link, with zero rebuild. Versions are
 * written by regenerate_site in src/api/admin.py right before each regeneration
 * overwrites the live config. */

const SLUG_PATTERN = /^[a-z0-9-]+$/;
const VERSION_PATTERN = /^\d+$/;

async function loadVersionConfig(slug: string, version: string): Promise<any | null> {
  if (!SLUG_PATTERN.test(slug) || !VERSION_PATTERN.test(version)) return null; // guards against path traversal
  const filePath = path.join(process.cwd(), "public", "previews", "versions", slug, `v${version}.json`);
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string; version: string }> }) {
  const { slug, version } = await params;
  const siteConfig = await loadVersionConfig(slug, version);
  if (!siteConfig) return {};
  return {
    title: `${siteConfig.name || slug} (v${version}) | Custom Web Preview`,
    description: siteConfig.scraped_tagline || siteConfig.heroSubtitle || undefined,
  };
}

export default async function SiteVersionPage({ params }: { params: Promise<{ slug: string; version: string }> }) {
  const { slug, version } = await params;
  const siteConfig = await loadVersionConfig(slug, version);
  if (!siteConfig) notFound();
  return (
    <DynamicClientSite
      siteConfig={siteConfig}
      versionBanner={{
        versionNumber: parseInt(version, 10),
        createdAt: siteConfig._archived_at || null,
        currentUrl: `/sites/${slug}`,
      }}
    />
  );
}
