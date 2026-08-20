'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Phone, MapPin, ShieldCheck, Sparkles, ArrowRight, Terminal, Zap } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, PrimaryButton, GhostButton, LiveBadge, Stars, AmbientGlow, MeshBackdrop } from '../site/ui';
import { LiveSlotPicker } from '../widgets/LiveSlotPicker';
import { siteCopy } from '../site/copy';

const DEFAULT_IMG =
  'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80';

function useHero() {
  const { config: c, theme: t, openBooking } = useSite();
  const cp = siteCopy(c);
  const img = c.design_system?.hero_image || DEFAULT_IMG;
  const badge = c.badgeText || `${String(c.industry || c.category || '').toUpperCase()} • ${String(c.city || '').toUpperCase()}`;
  const title = c.tagline || `${c.name} — Trusted ${c.industry || c.category} in ${c.city}`;
  const sub = c.heroSubtitle;
  return { c, t, openBooking, img, badge, title, sub, cp };
}

function RatingLine() {
  const { c, t } = useHero();
  return (
    <div className="flex items-center gap-3">
      <Stars />
      <span className="text-xs font-semibold" style={{ color: t.subtext }}>
        {c.google_rating} / 5.0 · {c.review_count}+ verified reviews
      </span>
    </div>
  );
}

/* A tasteful "built with AI" developer motif for tech archetypes. */
function CodeChip() {
  const { t } = useHero();
  return (
    <div
      className="font-mono text-[11px] rounded-lg border px-3 py-2 inline-flex items-center gap-2"
      style={{ borderColor: t.border, backgroundColor: withAlpha(t.text, 0.04), color: t.subtext }}
    >
      <Terminal className="w-3.5 h-3.5" style={{ color: t.accent }} />
      <span><span style={{ color: t.accent }}>ai</span>.book(<span style={{ color: t.badgeText }}>&quot;now&quot;</span>) → <span style={{ color: '#34d399' }}>confirmed</span></span>
    </div>
  );
}

/* ============================ 1. SPLIT SHOWCASE ============================ */
function SplitShowcase() {
  const { c, t, img, badge, title, sub } = useHero();
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 px-4 sm:px-8">
      <MeshBackdrop />
      <AmbientGlow className="top-10 -left-20" alpha={0.14} />
      <div className="max-w-7xl mx-auto grid lg:grid-cols-12 gap-12 items-center relative z-10">
        <div className="lg:col-span-7">
          <Reveal><div className="mb-7"><LiveBadge label={badge} /></div></Reveal>
          <Reveal delay={0.05}>
            <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold leading-[1.05] tracking-tight mb-7" style={{ fontFamily: t.serifFamily, color: t.text }}>
              {title}
            </h1>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-base sm:text-xl max-w-2xl leading-relaxed mb-9" style={{ color: t.subtext }}>{sub}</p>
          </Reveal>
          <Reveal delay={0.15}>
            <div className="flex flex-wrap items-center gap-4 mb-9">
              <PrimaryButton onClick={c._book}>Book Consultation</PrimaryButton>
              {c.phone && <GhostButton href={`tel:${c.phone}`}><Phone className="w-4 h-4" style={{ color: t.accent }} />{c.phone}</GhostButton>}
            </div>
          </Reveal>
          <Reveal delay={0.2}>
            <div className="pt-6" style={{ borderTop: `1px solid ${t.hairline}` }}><RatingLine /></div>
          </Reveal>
        </div>
        <Reveal delay={0.15} className="lg:col-span-5" y={40}>
          <motion.div
            whileHover={{ y: -6 }}
            transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            className={`relative overflow-hidden ${t.cardRadius} border shadow-2xl`}
            style={{ borderColor: t.border }}
          >
            <img src={img} alt={c.name} className="w-full h-[520px] object-cover" />
            <div className="absolute inset-0 flex flex-col justify-between p-7"
              style={{ background: `linear-gradient(to top, ${t.scrim(0.92)}, ${t.scrim(0.1)} 45%, transparent)` }}>
              <span className="self-end px-3.5 py-1.5 rounded-full text-xs font-bold inline-flex items-center gap-1.5"
                style={{ backgroundColor: t.scrim(0.7), color: '#34d399', border: `1px solid ${withAlpha('#34d399', 0.3)}` }}>
                <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#34d399' }} />
                Accepting New {siteCopy(c).audienceTitle}
              </span>
              <div className="p-5 rounded-2xl" style={{ backgroundColor: t.scrim(0.72), border: `1px solid ${withAlpha('#fff', 0.12)}`, backdropFilter: 'blur(12px)' }}>
                <Stars />
                <h3 className="text-lg font-bold mt-2" style={{ color: '#fff' }}>{c.name}</h3>
                <p className="text-xs mt-1" style={{ color: t.onImageSoft }}>{c.address || `${c.city}, ${c.country}`}</p>
              </div>
            </div>
          </motion.div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============================ 2. CENTERED LUXURY =========================== */
function CenteredLuxury() {
  const { c, t, badge, title, sub } = useHero();
  return (
    <section className="relative overflow-hidden py-24 sm:py-32 px-4 flex flex-col items-center text-center">
      <MeshBackdrop />
      <AmbientGlow className="top-24 left-1/2 -translate-x-1/2" size={640} alpha={0.16} />
      <div className="max-w-4xl mx-auto relative z-10 flex flex-col items-center">
        <Reveal><div className="mb-8"><LiveBadge label={badge} /></div></Reveal>
        <Reveal delay={0.05}>
          <h1 className="text-5xl sm:text-7xl font-extrabold leading-[1.05] tracking-tight mb-8" style={{ fontFamily: t.serifFamily, color: t.text }}>{title}</h1>
        </Reveal>
        <Reveal delay={0.1}><p className="text-lg sm:text-xl max-w-2xl leading-relaxed mb-9" style={{ color: t.subtext }}>{sub}</p></Reveal>
        <Reveal delay={0.15}>
          <div className="inline-flex items-center gap-3 border rounded-full px-6 py-2.5 mb-9 backdrop-blur-xl" style={{ borderColor: t.border, backgroundColor: withAlpha(t.text, 0.04) }}>
            <RatingLine />
          </div>
        </Reveal>
        <Reveal delay={0.2}><PrimaryButton onClick={c._book}>{siteCopy(c).bookLabel}</PrimaryButton></Reveal>
      </div>
    </section>
  );
}

/* ============================ 3. OFFSET BRUTALIST ========================= */
function OffsetBrutalist() {
  const { c, t, badge, title, sub } = useHero();
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 px-4 sm:px-8">
      <div className="max-w-6xl mx-auto relative z-10">
        <Reveal>
          <span className="inline-block font-mono text-xs font-bold uppercase tracking-widest px-4 py-2 mb-8"
            style={{ backgroundColor: t.accent, color: t.isDark ? '#000' : '#000', boxShadow: `6px 6px 0 ${t.primary}` }}>
            {badge}
          </span>
        </Reveal>
        <Reveal delay={0.05}>
          <h1 className="text-5xl sm:text-8xl font-extrabold leading-[0.95] tracking-tighter mb-8 uppercase" style={{ fontFamily: t.serifFamily, color: t.text }}>
            {title}
          </h1>
        </Reveal>
        <div className="grid md:grid-cols-2 gap-10 items-end">
          <Reveal delay={0.1}><p className="text-lg leading-relaxed" style={{ color: t.subtext }}>{sub}</p></Reveal>
          <Reveal delay={0.15} className="md:justify-self-end">
            <div className="flex flex-col gap-4">
              <div className="border-4 p-5" style={{ borderColor: t.text, boxShadow: `8px 8px 0 ${t.accent}` }}>
                <div className="text-4xl font-extrabold" style={{ color: t.text }}>{c.google_rating}★</div>
                <div className="text-xs font-bold uppercase tracking-wider" style={{ color: t.subtext }}>{c.review_count}+ reviews</div>
              </div>
              <PrimaryButton onClick={c._book}>Book Now</PrimaryButton>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ============================ 4. MINIMAL EDITORIAL ======================== */
function MinimalEditorial() {
  const { c, t, badge, title, sub, img } = useHero();
  return (
    <section className="relative py-20 sm:py-28 px-4 sm:px-8">
      <div className="max-w-6xl mx-auto relative z-10">
        <Reveal>
          <div className="flex items-center gap-4 text-xs font-medium tracking-[0.25em] uppercase mb-10" style={{ color: t.subtext }}>
            <span>{badge}</span>
            <span className="flex-1 h-px" style={{ backgroundColor: t.hairline }} />
            <span>Est. Excellence</span>
          </div>
        </Reveal>
        <Reveal delay={0.05}>
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-normal leading-[1.08] tracking-tight mb-10 max-w-4xl" style={{ fontFamily: t.serifFamily, color: t.text }}>
            {title}
          </h1>
        </Reveal>
        <div className="grid md:grid-cols-12 gap-12 items-start">
          <Reveal delay={0.1} className="md:col-span-7">
            <img src={img} alt={c.name} className={`w-full h-[420px] object-cover ${t.cardRadius}`} style={{ border: `1px solid ${t.border}` }} />
          </Reveal>
          <Reveal delay={0.15} className="md:col-span-5">
            <p className="text-lg leading-relaxed mb-8" style={{ color: t.subtext }}>{sub}</p>
            <div className="mb-8"><RatingLine /></div>
            <PrimaryButton onClick={c._book}>Request Consultation</PrimaryButton>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ============================ 5. BENTO GRID =============================== */
function BentoGrid() {
  const { c, t, badge, title, sub, img } = useHero();
  const stats = (c.stats || []).slice(0, 2);
  return (
    <section className="relative overflow-hidden py-16 sm:py-24 px-4 sm:px-8">
      <MeshBackdrop grid={false} />
      <div className="max-w-7xl mx-auto relative z-10">
        <Reveal><div className="mb-8"><LiveBadge label={badge} /></div></Reveal>
        <div className="grid md:grid-cols-3 gap-4 auto-rows-[minmax(0,1fr)]">
          <Reveal className="md:col-span-2 md:row-span-2">
            <div className={`h-full p-8 sm:p-10 ${t.cardRadius} border flex flex-col justify-between`}
              style={{ borderColor: t.border, background: `linear-gradient(160deg, ${withAlpha(t.primary, t.isDark ? 0.22 : 0.08)}, ${t.surface})` }}>
              <h1 className="text-4xl sm:text-6xl font-extrabold leading-[1.05] tracking-tight" style={{ fontFamily: t.serifFamily, color: t.text }}>{title}</h1>
              <div>
                <p className="text-base sm:text-lg leading-relaxed mb-7 max-w-xl" style={{ color: t.subtext }}>{sub}</p>
                <div className="flex flex-wrap gap-4 items-center">
                  <PrimaryButton onClick={c._book}>Book Consultation</PrimaryButton>
                  {c.phone && <GhostButton href={`tel:${c.phone}`}><Phone className="w-4 h-4" style={{ color: t.accent }} />Call</GhostButton>}
                </div>
              </div>
            </div>
          </Reveal>
          <Reveal delay={0.08}>
            <div className={`relative overflow-hidden ${t.cardRadius} border h-full min-h-[200px]`} style={{ borderColor: t.border }}>
              <img src={img} alt={c.name} className="absolute inset-0 w-full h-full object-cover" />
              <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${t.scrim(0.85)}, transparent)` }} />
              <div className="absolute bottom-4 left-4"><Stars /></div>
            </div>
          </Reveal>
          {stats.map((s: any, i: number) => (
            <Reveal key={i} delay={0.12 + i * 0.06}>
              <div className={`h-full p-6 ${t.cardRadius} border flex flex-col justify-center`} style={{ borderColor: t.border, backgroundColor: t.surface }}>
                <div className="text-3xl font-extrabold" style={{ fontFamily: t.serifFamily, color: t.accent }}>{s.number}</div>
                <div className="text-[11px] font-bold uppercase tracking-widest mt-1" style={{ color: t.subtext }}>{s.label}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ============================ 6. SIDE FORM =============================== */
function SideForm() {
  const { c, t, badge, title, sub, openBooking } = useHero();
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 px-4 sm:px-8">
      <MeshBackdrop />
      <AmbientGlow className="-top-10 right-0" alpha={0.14} />
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-14 items-center relative z-10">
        <div>
          <Reveal><div className="mb-7"><LiveBadge label={badge} /></div></Reveal>
          <Reveal delay={0.05}><h1 className="text-4xl sm:text-6xl font-extrabold leading-[1.05] tracking-tight mb-7" style={{ fontFamily: t.serifFamily, color: t.text }}>{title}</h1></Reveal>
          <Reveal delay={0.1}><p className="text-base sm:text-xl leading-relaxed mb-8" style={{ color: t.subtext }}>{sub}</p></Reveal>
          <Reveal delay={0.15}><div className="mb-2"><RatingLine /></div></Reveal>
        </div>
        <Reveal delay={0.15} y={40}>
          <LiveSlotPicker cityName={c.city} accentColor={t.accent} onSlotSelected={openBooking} />
        </Reveal>
      </div>
    </section>
  );
}

/* ============================ 7. CREAM HERITAGE ========================== */
function CreamHeritage() {
  const { c, t, badge, title, sub } = useHero();
  return (
    <section className="relative py-24 sm:py-32 px-4 flex flex-col items-center text-center">
      <AmbientGlow className="top-20 left-1/2 -translate-x-1/2" size={560} alpha={0.10} />
      <div className="max-w-3xl mx-auto relative z-10 flex flex-col items-center">
        <Reveal>
          <span className="text-xs font-semibold tracking-[0.3em] uppercase mb-8" style={{ color: t.accent }}>{badge}</span>
        </Reveal>
        <Reveal delay={0.05}>
          <h1 className="text-5xl sm:text-7xl leading-[1.05] mb-8 italic" style={{ fontFamily: t.serifFamily, color: t.text, fontWeight: 500 }}>{title}</h1>
        </Reveal>
        <Reveal delay={0.1}><p className="text-lg leading-relaxed mb-9 max-w-xl" style={{ color: t.subtext }}>{sub}</p></Reveal>
        <Reveal delay={0.15}>
          <div className="flex items-center gap-4 mb-9">
            <div className="flex -space-x-3">
              {['A', 'S', 'M', 'J'].map((l, i) => (
                <div key={i} className="w-10 h-10 rounded-full border-2 flex items-center justify-center font-bold text-white text-xs"
                  style={{ borderColor: t.bg, backgroundColor: [t.primary, t.accent, t.primaryHover, t.primary][i] }}>{l}</div>
              ))}
            </div>
            <div className="text-left"><Stars /><span className="text-xs" style={{ color: t.subtext }}>Loved by {c.review_count}+ {siteCopy(c).audience}</span></div>
          </div>
        </Reveal>
        <Reveal delay={0.2}><PrimaryButton onClick={c._book}>{siteCopy(c).bookLabel}</PrimaryButton></Reveal>
      </div>
    </section>
  );
}

/* ============================ 8. CYBER GLOW ============================== */
function CyberGlow() {
  const { c, t, badge, title, sub } = useHero();
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 px-4 sm:px-8">
      <MeshBackdrop />
      <AmbientGlow className="top-0 left-1/4" color={withAlpha(t.primary, 0.22)} />
      <AmbientGlow className="bottom-0 right-1/4" color={withAlpha(t.accent, 0.18)} />
      <div className="max-w-5xl mx-auto text-center relative z-10 flex flex-col items-center">
        <Reveal><div className="mb-6"><CodeChip /></div></Reveal>
        <Reveal delay={0.05}><div className="mb-7"><LiveBadge label={badge} /></div></Reveal>
        <Reveal delay={0.1}>
          <h1 className="text-5xl sm:text-7xl font-extrabold leading-[1.03] tracking-tight mb-7" style={{ fontFamily: t.serifFamily, color: t.text }}>
            {title}
          </h1>
        </Reveal>
        <Reveal delay={0.15}><p className="text-lg leading-relaxed mb-9 max-w-2xl" style={{ color: t.subtext }}>{sub}</p></Reveal>
        <Reveal delay={0.2}>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <PrimaryButton onClick={c._book}>Book Instantly</PrimaryButton>
            <div className="inline-flex items-center gap-2 text-xs font-mono px-4 py-3 rounded-lg border" style={{ borderColor: t.border, color: t.subtext }}>
              <Zap className="w-4 h-4" style={{ color: t.accent }} /> {c.google_rating}★ · {c.review_count}+ reviews
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============================ 9. MAGAZINE COVER ========================== */
function MagazineCover() {
  const { c, t, badge, title, sub, img } = useHero();
  return (
    <section className="relative overflow-hidden min-h-[85vh] flex items-end">
      <img src={img} alt={c.name} className="absolute inset-0 w-full h-full object-cover" />
      <div className="absolute inset-0" style={{ background: `linear-gradient(to top, ${t.scrim(0.96)} 8%, ${t.scrim(0.55)} 45%, ${t.scrim(0.35)})` }} />
      <div className="relative z-10 max-w-7xl mx-auto w-full px-4 sm:px-8 pb-20 pt-32">
        <Reveal>
          <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full text-[11px] font-bold tracking-widest uppercase mb-6 border backdrop-blur-md"
            style={{ backgroundColor: withAlpha('#000', 0.4), color: '#fff', borderColor: withAlpha('#fff', 0.25) }}>
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: '#34d399' }} />{badge}
          </div>
        </Reveal>
        <Reveal delay={0.05}>
          <h1 className="text-5xl sm:text-7xl md:text-8xl font-extrabold leading-[0.98] tracking-tight mb-7 max-w-4xl" style={{ fontFamily: t.serifFamily, color: '#fff' }}>{title}</h1>
        </Reveal>
        <Reveal delay={0.1}><p className="text-lg sm:text-xl leading-relaxed mb-9 max-w-2xl" style={{ color: t.onImageSoft }}>{sub}</p></Reveal>
        <Reveal delay={0.15}>
          <div className="flex flex-wrap items-center gap-5">
            <PrimaryButton onClick={c._book}>Book Consultation</PrimaryButton>
            <div className="flex items-center gap-3"><Stars /><span className="text-sm font-semibold" style={{ color: '#fff' }}>{c.google_rating} · {c.review_count}+ reviews</span></div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============================ 10. COMPACT BAR =========================== */
function CompactBar() {
  const { c, t, badge, title, sub } = useHero();
  return (
    <section className="relative overflow-hidden py-14 sm:py-16 px-4 sm:px-8">
      <MeshBackdrop grid={false} />
      <div className="max-w-6xl mx-auto relative z-10">
        <div className={`p-8 sm:p-10 ${t.cardRadius} border flex flex-col lg:flex-row lg:items-center gap-8 justify-between`}
          style={{ borderColor: t.border, background: `linear-gradient(120deg, ${withAlpha(t.primary, t.isDark ? 0.2 : 0.06)}, ${t.surface})` }}>
          <div className="max-w-2xl">
            <Reveal><div className="mb-4"><LiveBadge label={badge} /></div></Reveal>
            <Reveal delay={0.05}><h1 className="text-3xl sm:text-5xl font-extrabold leading-[1.06] tracking-tight mb-3" style={{ fontFamily: t.serifFamily, color: t.text }}>{title}</h1></Reveal>
            <Reveal delay={0.1}><p className="text-sm sm:text-base leading-relaxed" style={{ color: t.subtext }}>{sub}</p></Reveal>
          </div>
          <Reveal delay={0.12}>
            <div className="flex flex-col gap-3 shrink-0">
              <PrimaryButton onClick={c._book} full>{siteCopy(c).bookLabel}</PrimaryButton>
              {c.phone && (
                <a href={`tel:${c.phone}`} className="text-center text-sm font-bold inline-flex items-center justify-center gap-2" style={{ color: t.accent }}>
                  <Phone className="w-4 h-4" /> {c.phone}
                </a>
              )}
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

const HEROES: Record<string, React.FC> = {
  HERO_SPLIT_SHOWCASE: SplitShowcase,
  HERO_CENTERED_LUXURY: CenteredLuxury,
  HERO_OFFSET_BRUTALIST: OffsetBrutalist,
  HERO_MINIMAL_EDITORIAL: MinimalEditorial,
  HERO_BENTO_GRID: BentoGrid,
  HERO_SIDE_FORM: SideForm,
  HERO_CREAM_HERITAGE: CreamHeritage,
  HERO_CYBER_GLOW: CyberGlow,
  HERO_MAGAZINE_COVER: MagazineCover,
  HERO_COMPACT_BAR: CompactBar,
};

export default function Hero() {
  const { config, openBooking } = useSite();
  // expose booking to leaf helpers without prop-drilling through useHero
  config._book = openBooking;
  const variant = config.layout_tree?.variants?.hero || 'HERO_SPLIT_SHOWCASE';
  const Cmp = HEROES[variant] || SplitShowcase;
  return <Cmp />;
}
