'use client';

import React from 'react';
import { Sparkles, Clock, ShieldCheck, Zap, Award, Heart } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { Reveal, Stagger, StaggerItem, SectionHeading, Section, Card } from '../site/ui';

const ICONS: Record<string, React.ReactNode> = {
  sparkles: <Sparkles className="w-6 h-6" />,
  clock: <Clock className="w-6 h-6" />,
  shield: <ShieldCheck className="w-6 h-6" />,
  zap: <Zap className="w-6 h-6" />,
  award: <Award className="w-6 h-6" />,
  heart: <Heart className="w-6 h-6" />,
};

export function TrustRibbon() {
  const { config: c, theme: t } = useSite();
  const stats = c.stats || [];
  if (!stats.length) return null;
  return (
    <Section tint>
      <Stagger className="grid grid-cols-2 md:grid-cols-4 gap-5" stagger={0.07}>
        {stats.map((s: any, i: number) => (
          <StaggerItem key={i}>
            <Card className="p-5 text-center h-full">
              <div className="text-xl sm:text-3xl font-extrabold" style={{ fontFamily: t.serifFamily, color: t.accent }}>{s.number}</div>
              <div className="text-[11px] font-bold uppercase tracking-widest mt-3" style={{ color: t.subtext }}>{s.label}</div>
            </Card>
          </StaggerItem>
        ))}
      </Stagger>
    </Section>
  );
}

export function Usps() {
  const { config: c, theme: t } = useSite();
  const usps = c.usps || [];
  if (!usps.length) return null;
  const audience = (c.audience_noun || 'Clients');
  const audienceTitle = audience.charAt(0).toUpperCase() + audience.slice(1);
  return (
    <Section id="why-us" tint>
      <Reveal><SectionHeading eyebrow="Why us" title={`Why ${audienceTitle} Trust`} accent={c.name} /></Reveal>
      <Stagger className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {usps.map((u: any, i: number) => (
          <StaggerItem key={i}>
            <Card className="p-5 h-full">
              <div className="w-12 h-12 rounded-2xl border flex items-center justify-center mb-4" style={{ borderColor: t.border, backgroundColor: t.badgeBg, color: t.accent }}>
                {ICONS[u.icon] || <Sparkles className="w-6 h-6" />}
              </div>
              <h3 className="text-base font-bold mb-3" style={{ fontFamily: t.serifFamily, color: t.text }}>{u.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: t.subtext }}>{u.description}</p>
            </Card>
          </StaggerItem>
        ))}
      </Stagger>
    </Section>
  );
}

