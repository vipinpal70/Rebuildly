'use client';

import React, { useState, useMemo } from 'react';
import { BookingModal } from './BookingModal';
import { ChatbotWidget } from './ChatbotWidget';
import { SiteProvider } from './site/SiteProvider';
import { buildTheme } from './site/theme';
import { SECTION_REGISTRY, DEFAULT_ORDER } from './site/registry';
import { TopStrip, Header, Footer } from './sections/Chrome';

interface DynamicClientSiteProps {
  siteConfig: any;
  /** Set only by the /sites/{slug}/v/{n} historical route — renders a small
   * fixed banner so an old version is never mistaken for the live site,
   * whether it's the admin or a client following a shared link. */
  versionBanner?: { versionNumber: number; createdAt: string | null; currentUrl: string };
}

// Thin orchestrator: derive the theme once, then render whichever section
// variants the generator selected (in the order it chose). All visual identity
// lives in the theme + individual section components — nothing is hardcoded here.
export default function DynamicClientSite({ siteConfig, versionBanner }: DynamicClientSiteProps) {
  const [isBookingOpen, setBookingOpen] = useState(false);

  const design = siteConfig.design_system || {};
  const theme = useMemo(
    () => buildTheme(design.colors || {}, design.card_radius, design.btn_radius),
    [design]
  );

  const order: string[] = siteConfig.layout_tree?.section_order || DEFAULT_ORDER;

  return (
    <SiteProvider value={{ config: siteConfig, theme, openBooking: () => setBookingOpen(true) }}>
      <main
        className="min-h-screen relative antialiased"
        style={{
          backgroundColor: theme.bg,
          color: theme.text,
          fontFamily: theme.sansFamily,
          // expose palette as CSS vars for any child that prefers them
          ['--c-bg' as any]: theme.bg,
          ['--c-text' as any]: theme.text,
          ['--c-subtext' as any]: theme.subtext,
          ['--c-primary' as any]: theme.primary,
          ['--c-accent' as any]: theme.accent,
          ['--c-border' as any]: theme.border,
        }}
      >
        {design.google_fonts_url && <link rel="stylesheet" href={design.google_fonts_url} />}

        {versionBanner && (
          <div className="sticky top-0 z-60 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 px-4 py-2 text-xs font-semibold text-center bg-amber-500 text-amber-950">
            <span>
              Viewing version {versionBanner.versionNumber}
              {versionBanner.createdAt ? ` · ${new Date(versionBanner.createdAt).toLocaleDateString()}` : ''} — this is not the current version.
            </span>
            <a href={versionBanner.currentUrl} className="underline underline-offset-2 hover:opacity-80">
              View current version →
            </a>
          </div>
        )}

        <TopStrip />
        <Header />

        {order.map((key, i) => {
          const Section = SECTION_REGISTRY[key];
          return Section ? <Section key={`${key}-${i}`} /> : null;
        })}

        <Footer />

        <BookingModal
          business={siteConfig}
          isOpen={isBookingOpen}
          onClose={() => setBookingOpen(false)}
          primaryGradient={theme.primaryGradient}
        />
        <ChatbotWidget business={siteConfig} primaryGradient={theme.primaryGradient} glowShadow={theme.glow(0.4)} />
      </main>
    </SiteProvider>
  );
}
