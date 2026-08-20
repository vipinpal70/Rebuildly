'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Sparkles, ArrowRight, Plus, Minus, Star } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, Stagger, StaggerItem, SectionHeading, Section, Card, PrimaryButton } from '../site/ui';
import { siteCopy } from '../site/copy';

function useServices() {
  const { config: c, theme: t, openBooking } = useSite();
  const services = c.detailedServices || [];
  const cats: string[] = ['ALL', ...Array.from(new Set(services.map((s: any) => String(s.category)))) as string[]];
  return { c, t, openBooking, services, cats, cp: siteCopy(c) };
}

function FeatureList({ features }: { features?: string[] }) {
  const { theme: t } = useSite();
  if (!features?.length) return null;
  return (
    <ul className="space-y-2.5 text-xs" style={{ color: t.text }}>
      {features.map((f, i) => (
        <li key={i} className="flex items-center gap-2.5">
          <Check className="w-4 h-4 shrink-0" style={{ color: t.accent }} /><span>{f}</span>
        </li>
      ))}
    </ul>
  );
}

function CatBadge({ children }: { children: React.ReactNode }) {
  const { theme: t } = useSite();
  return (
    <span className="text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border inline-block"
      style={{ backgroundColor: t.badgeBg, color: t.badgeText, borderColor: t.border }}>{children}</span>
  );
}

const HEAD = { eyebrow: 'What we offer', icon: <Sparkles className="w-4 h-4" />, title: 'Our', accent: 'Services' };

/* ------------------------------ grid + pills ------------------------------ */
function GridCards({ pills, icons }: { pills?: boolean; icons?: boolean }) {
  const { c, t, openBooking, services, cats } = useServices();
  const [active, setActive] = useState('ALL');
  const list = active === 'ALL' ? services : services.filter((s: any) => s.category === active);
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      {pills && cats.length > 2 && (
        <Reveal delay={0.05}>
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {cats.map((cat) => (
              <button key={cat} onClick={() => setActive(cat)}
                className="px-5 py-2.5 rounded-full text-xs font-bold border transition-all cursor-pointer"
                style={active === cat
                  ? { background: t.primaryGradient, color: '#fff', borderColor: 'transparent' }
                  : { color: t.subtext, borderColor: t.border, backgroundColor: 'transparent' }}>{cat}</button>
            ))}
          </div>
        </Reveal>
      )}
      <Stagger className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence mode="popLayout">
          {list.map((s: any, i: number) => (
            <StaggerItem key={s.title + i}>
              <Card className="p-8 h-full flex flex-col justify-between">
                <div>
                  {icons
                    ? <div className="w-12 h-12 rounded-2xl border flex items-center justify-center mb-5" style={{ borderColor: t.border, backgroundColor: t.badgeBg }}><Sparkles className="w-6 h-6" style={{ color: t.accent }} /></div>
                    : <div className="mb-5"><CatBadge>{s.category}</CatBadge></div>}
                  <h3 className="text-xl font-bold mb-2" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h3>
                  {s.priceFrom && <div className="text-sm font-bold mb-3" style={{ color: t.accent }}>From {s.priceFrom}</div>}
                  <p className="text-sm leading-relaxed mb-6" style={{ color: t.subtext }}>{s.description}</p>
                  <div className="pt-4 mb-6" style={{ borderTop: `1px solid ${t.hairline}` }}><FeatureList features={s.features} /></div>
                </div>
                <button onClick={openBooking} className={`w-full py-3.5 ${t.btnRadius} text-xs font-bold border transition-colors cursor-pointer inline-flex items-center justify-center gap-2`}
                  style={{ borderColor: t.border, color: t.text, backgroundColor: withAlpha(t.text, 0.03) }}>
                  {siteCopy(c).enquireLabel} <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </Card>
            </StaggerItem>
          ))}
        </AnimatePresence>
      </Stagger>
    </Section>
  );
}

/* -------------------------------- bento ---------------------------------- */
function BentoTiles() {
  const { c, t, openBooking, services } = useServices();
  const [hero, ...rest] = services;
  if (!hero) return <GridCards />;
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      <div className="grid md:grid-cols-3 gap-5">
        <Reveal className="md:col-span-3 lg:col-span-1 lg:row-span-2">
          <div className={`h-full p-9 ${t.cardRadius} border flex flex-col justify-between`}
            style={{ borderColor: t.border, background: `linear-gradient(160deg, ${withAlpha(t.primary, t.isDark ? 0.28 : 0.1)}, ${t.surface})` }}>
            <div>
              <CatBadge>{hero.category} · Signature</CatBadge>
              <h3 className="text-3xl font-bold my-4" style={{ fontFamily: t.serifFamily, color: t.text }}>{hero.title}</h3>
              <p className="text-sm leading-relaxed mb-6" style={{ color: t.subtext }}>{hero.description}</p>
              <FeatureList features={hero.features} />
            </div>
            <div className="mt-8"><PrimaryButton onClick={openBooking}>{siteCopy(c).enquireLabel}</PrimaryButton></div>
          </div>
        </Reveal>
        <Stagger className="md:col-span-3 lg:col-span-2 grid sm:grid-cols-2 gap-5">
          {rest.map((s: any, i: number) => (
            <StaggerItem key={i}>
              <Card className="p-7 h-full">
                <div className="mb-4"><CatBadge>{s.category}</CatBadge></div>
                <h3 className="text-lg font-bold mb-2" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h3>
                <p className="text-xs leading-relaxed" style={{ color: t.subtext }}>{s.description}</p>
              </Card>
            </StaggerItem>
          ))}
        </Stagger>
      </div>
    </Section>
  );
}

/* ------------------------------- side tabs -------------------------------- */
function SideTabs() {
  const { c, t, openBooking, services } = useServices();
  const [idx, setIdx] = useState(0);
  const s = services[idx];
  if (!s) return <GridCards />;
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} center={false} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      <div className="grid lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 flex flex-col gap-2">
          {services.map((sv: any, i: number) => (
            <button key={i} onClick={() => setIdx(i)}
              className={`text-left p-5 ${t.cardRadius} border transition-all cursor-pointer`}
              style={i === idx
                ? { borderColor: t.accent, backgroundColor: t.badgeBg }
                : { borderColor: t.border, backgroundColor: 'transparent' }}>
              <div className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: t.accent }}>{String(i + 1).padStart(2, '0')}</div>
              <div className="font-bold" style={{ color: t.text }}>{sv.title}</div>
            </button>
          ))}
        </div>
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            <motion.div key={idx} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -16 }} transition={{ duration: 0.35 }}>
              <Card hover={false} className="p-9">
                <div className="mb-4"><CatBadge>{s.category}</CatBadge></div>
                <h3 className="text-3xl font-bold mb-4" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h3>
                <p className="text-base leading-relaxed mb-7" style={{ color: t.subtext }}>{s.description}</p>
                <div className="grid sm:grid-cols-2 gap-3 mb-8"><FeatureList features={s.features} /></div>
                <PrimaryButton onClick={openBooking}>{siteCopy(c).enquireLabel} {s.title}</PrimaryButton>
              </Card>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </Section>
  );
}

/* ------------------------------- accordion -------------------------------- */
function AccordionList() {
  const { c, t, openBooking, services } = useServices();
  const [open, setOpen] = useState(0);
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      <div className="max-w-4xl mx-auto space-y-4">
        {services.map((s: any, i: number) => {
          const isOpen = open === i;
          return (
            <Reveal key={i} delay={i * 0.04}>
              <Card hover={false} className="overflow-hidden">
                <button onClick={() => setOpen(isOpen ? -1 : i)} className="w-full p-6 flex items-center justify-between gap-4 cursor-pointer text-left">
                  <div className="flex items-center gap-4">
                    <span className="text-2xl font-extrabold" style={{ fontFamily: t.serifFamily, color: t.accent }}>{String(i + 1).padStart(2, '0')}</span>
                    <span className="text-lg font-bold" style={{ color: t.text }}>{s.title}</span>
                  </div>
                  {isOpen ? <Minus className="w-5 h-5" style={{ color: t.accent }} /> : <Plus className="w-5 h-5" style={{ color: t.accent }} />}
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
                      <div className="px-6 pb-6 pl-16 grid sm:grid-cols-2 gap-6" style={{ borderTop: `1px solid ${t.hairline}` }}>
                        <p className="text-sm leading-relaxed pt-4" style={{ color: t.subtext }}>{s.description}</p>
                        <div className="pt-4"><FeatureList features={s.features} /></div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            </Reveal>
          );
        })}
      </div>
    </Section>
  );
}

/* ---------------------------- highlight banner ---------------------------- */
function HighlightBanner() {
  const { c, t, openBooking, services } = useServices();
  const [hero, ...rest] = services;
  if (!hero) return <GridCards />;
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      <Reveal>
        <div className={`p-9 sm:p-12 ${t.cardRadius} relative overflow-hidden mb-6`}
          style={{ background: t.primaryGradient, color: '#fff' }}>
          <div className="absolute -top-16 -right-16 w-72 h-72 rounded-full blur-3xl" style={{ backgroundColor: withAlpha('#fff', 0.15) }} />
          <div className="relative z-10 grid md:grid-cols-2 gap-8 items-center">
            <div>
              <span className="inline-block text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full mb-4" style={{ backgroundColor: withAlpha('#fff', 0.2) }}>Most Requested</span>
              <h3 className="text-3xl sm:text-4xl font-bold mb-2" style={{ fontFamily: t.serifFamily }}>{hero.title}</h3>
              {hero.priceFrom && <div className="text-sm font-bold mb-4 opacity-90">From {hero.priceFrom}</div>}
              <p className="text-sm leading-relaxed opacity-90 mb-6">{hero.description}</p>
              <button onClick={openBooking} className={`px-7 py-3.5 ${t.btnRadius} text-sm font-bold cursor-pointer`} style={{ backgroundColor: '#fff', color: t.primary }}>{siteCopy(c).enquireLabel} {hero.title}</button>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {(hero.features || []).map((f: string, i: number) => (
                <div key={i} className="flex items-center gap-3 p-3 rounded-xl" style={{ backgroundColor: withAlpha('#fff', 0.12) }}>
                  <Check className="w-4 h-4" /><span className="text-sm font-medium">{f}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Reveal>
      <Stagger className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
        {rest.map((s: any, i: number) => (
          <StaggerItem key={i}>
            <Card className="p-7 h-full">
              <div className="mb-4"><CatBadge>{s.category}</CatBadge></div>
              <h4 className="text-lg font-bold mb-1" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h4>
              {s.priceFrom && <div className="text-xs font-bold mb-2" style={{ color: t.accent }}>From {s.priceFrom}</div>}
              <p className="text-xs leading-relaxed" style={{ color: t.subtext }}>{s.description}</p>
            </Card>
          </StaggerItem>
        ))}
      </Stagger>
    </Section>
  );
}

/* --------------------------- comparison matrix ---------------------------- */
function ComparisonTable() {
  const { c, t, openBooking, services } = useServices();
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} accent="Services" subtitle={`Compare our services across ${c.city}.`} /></Reveal>
      <Reveal>
        <Card hover={false} className="overflow-hidden">
          <div className="grid" style={{ gridTemplateColumns: `1.4fr repeat(2, 1fr)` }}>
            <div className="p-5" />
            <div className="p-5 text-center" style={{ borderLeft: `1px solid ${t.hairline}` }}><div className="text-xs font-bold uppercase tracking-wider" style={{ color: t.subtext }}>Standard Care</div></div>
            <div className="p-5 text-center" style={{ borderLeft: `1px solid ${t.hairline}`, backgroundColor: t.badgeBg }}><div className="text-xs font-bold uppercase tracking-wider" style={{ color: t.badgeText }}>{c.name}</div></div>
            {services.slice(0, 5).map((s: any, i: number) => (
              <React.Fragment key={i}>
                <div className="p-5 text-sm font-semibold" style={{ borderTop: `1px solid ${t.hairline}`, color: t.text }}>{s.title}</div>
                <div className="p-5 text-center" style={{ borderTop: `1px solid ${t.hairline}`, borderLeft: `1px solid ${t.hairline}` }}><span style={{ color: t.subtext }}>—</span></div>
                <div className="p-5 text-center" style={{ borderTop: `1px solid ${t.hairline}`, borderLeft: `1px solid ${t.hairline}`, backgroundColor: withAlpha(t.accent, 0.05) }}><Check className="w-5 h-5 inline" style={{ color: t.accent }} /></div>
              </React.Fragment>
            ))}
          </div>
        </Card>
      </Reveal>
      <Reveal delay={0.1}><div className="text-center mt-10"><PrimaryButton onClick={openBooking}>Choose {c.name}</PrimaryButton></div></Reveal>
    </Section>
  );
}

/* --------------------------- magazine split ------------------------------- */
function MagazineSplit() {
  const { c, t, openBooking, services } = useServices();
  const img = c.design_system?.hero_image;
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} subtitle={`Professional services tailored for ${c.city}.`} /></Reveal>
      <div className="space-y-6">
        {services.map((s: any, i: number) => (
          <Reveal key={i} delay={i * 0.05}>
            <Card hover={false} className={`overflow-hidden grid md:grid-cols-2 ${i % 2 ? 'md:[direction:rtl]' : ''}`}>
              <div className="p-9 [direction:ltr]">
                <div className="mb-4"><CatBadge>{s.category}</CatBadge></div>
                <h3 className="text-2xl font-bold mb-3" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h3>
                <p className="text-sm leading-relaxed mb-6" style={{ color: t.subtext }}>{s.description}</p>
                <FeatureList features={s.features} />
              </div>
              <div className="min-h-[220px] relative [direction:ltr]" style={{ backgroundColor: t.badgeBg }}>
                {img && <img src={img} alt={s.title} className="absolute inset-0 w-full h-full object-cover opacity-90" />}
              </div>
            </Card>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

/* ------------------------------- carousel --------------------------------- */
function Carousel() {
  const { c, t, openBooking, services } = useServices();
  return (
    <Section id="services">
      <Reveal><SectionHeading {...HEAD} center={false} subtitle={`Swipe through our specialties in ${c.city}.`} /></Reveal>
      <div className="flex gap-5 overflow-x-auto pb-6 snap-x" style={{ scrollbarWidth: 'thin' }}>
        {services.map((s: any, i: number) => (
          <div key={i} className="snap-start shrink-0 w-[300px]">
            <Card className="p-7 h-full">
              <div className="mb-4"><CatBadge>{s.category}</CatBadge></div>
              <h3 className="text-lg font-bold mb-2" style={{ fontFamily: t.serifFamily, color: t.text }}>{s.title}</h3>
              <p className="text-xs leading-relaxed mb-5" style={{ color: t.subtext }}>{s.description}</p>
              <FeatureList features={s.features} />
            </Card>
          </div>
        ))}
      </div>
    </Section>
  );
}

const MAP: Record<string, React.FC> = {
  SERVICES_3COL_CARDS: () => <GridCards />,
  SERVICES_ICON_BOXES: () => <GridCards icons />,
  SERVICES_MODERN_PILLS: () => <GridCards pills />,
  SERVICES_BENTO_TILES: BentoTiles,
  SERVICES_SIDE_TABS: SideTabs,
  SERVICES_ACCORDION_LIST: AccordionList,
  SERVICES_HIGHLIGHT_BANNER: HighlightBanner,
  SERVICES_COMPARISON_TABLE: ComparisonTable,
  SERVICES_MAGAZINE_SPLIT: MagazineSplit,
  SERVICES_CAROUSEL_CARDS: Carousel,
};

export default function Services() {
  const { config } = useSite();
  const v = config.layout_tree?.variants?.services || 'SERVICES_3COL_CARDS';
  const Cmp = MAP[v] || (() => <GridCards />);
  return <Cmp />;
}
