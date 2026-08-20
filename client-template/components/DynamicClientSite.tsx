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
}

// Thin orchestrator: derive the theme once, then render whichever section
// variants the generator selected (in the order it chose). All visual identity
// lives in the theme + individual section components — nothing is hardcoded here.
export default function DynamicClientSite({ siteConfig }: DynamicClientSiteProps) {
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

        <TopStrip />
        <Header />

        {order.map((key, i) => {
          const Section = SECTION_REGISTRY[key];
          return Section ? <Section key={`${key}-${i}`} /> : null;
        })}

        <Footer />

        <BookingModal business={siteConfig} isOpen={isBookingOpen} onClose={() => setBookingOpen(false)} />
        <ChatbotWidget business={siteConfig} />
      </main>
    </SiteProvider>
  );
}
