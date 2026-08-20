'use client';

import React from 'react';
import { Phone, Calendar, Star, ArrowRight } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, Section, PrimaryButton, GhostButton, AmbientGlow, Stars } from '../site/ui';
import { LiveSlotPicker } from '../widgets/LiveSlotPicker';
import { siteCopy } from '../site/copy';

function useCta() {
  const { config: c, theme: t, openBooking } = useSite();
  return { c, t, openBooking, cp: siteCopy(c) };
}

function RadialGlow() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <div className="relative text-center">
        <AmbientGlow className="top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" size={520} alpha={0.18} />
        <Reveal>
          <div className={`max-w-4xl mx-auto p-12 sm:p-16 ${t.cardRadius} border relative z-10`}
            style={{ backgroundColor: t.surface, borderColor: t.border, backdropFilter: t.isDark ? 'blur(16px)' : undefined }}>
            <div className="flex justify-center mb-6"><Stars className="w-5 h-5" /></div>
            <h2 className="text-3xl sm:text-5xl font-bold mb-5" style={{ fontFamily: t.serifFamily, color: t.text }}>Get Started with {c.name}</h2>
            <p className="text-base max-w-xl mx-auto mb-9 leading-relaxed" style={{ color: t.subtext }}>
              Experience {cp.audience}-focused service from our team in {c.city}. Reach out online in under 60 seconds.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <PrimaryButton onClick={openBooking}>{cp.bookLabel}</PrimaryButton>
              {c.phone && <GhostButton href={`tel:${c.phone}`}><Phone className="w-4 h-4" style={{ color: t.accent }} />{c.phone}</GhostButton>}
            </div>
          </div>
        </Reveal>
      </div>
    </Section>
  );
}

function SplitAppointment() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <div className="grid lg:grid-cols-2 gap-12 items-center">
        <Reveal>
          <h2 className="text-3xl sm:text-5xl font-bold mb-5" style={{ fontFamily: t.serifFamily, color: t.text }}>Your {cp.bookingNoun}, one tap away</h2>
          <p className="text-base leading-relaxed mb-8" style={{ color: t.subtext }}>
            Pick a time online or call our team directly in {c.city}.
          </p>
          {c.phone && (
            <a href={`tel:${c.phone}`} className={`inline-flex items-center gap-4 p-5 ${t.cardRadius} border`} style={{ borderColor: t.border, backgroundColor: t.surface }}>
              <span className="w-12 h-12 rounded-full flex items-center justify-center" style={{ background: t.primaryGradient }}><Phone className="w-5 h-5 text-white" /></span>
              <span><span className="block text-xs uppercase tracking-wider" style={{ color: t.subtext }}>Call now</span><span className="text-xl font-bold" style={{ color: t.text }}>{c.phone}</span></span>
            </a>
          )}
        </Reveal>
        <Reveal delay={0.1} y={40}><LiveSlotPicker cityName={c.city} accentColor={t.accent} onSlotSelected={openBooking} /></Reveal>
      </div>
    </Section>
  );
}

function FullWidthGradient() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <section className="relative overflow-hidden py-24 px-4 sm:px-8" style={{ background: t.primaryGradient }}>
      <div className="absolute -top-20 -right-10 w-96 h-96 rounded-full blur-3xl" style={{ backgroundColor: withAlpha('#fff', 0.15) }} />
      <Reveal>
        <div className="max-w-4xl mx-auto text-center relative z-10" style={{ color: '#fff' }}>
          <h2 className="text-4xl sm:text-6xl font-bold mb-5" style={{ fontFamily: t.serifFamily }}>Ready to get started?</h2>
          <p className="text-lg opacity-90 max-w-xl mx-auto mb-9">Join {c.review_count}+ happy {cp.audience} in {c.city}. Get in touch today.</p>
          <div className="flex flex-wrap justify-center gap-4">
            <button onClick={openBooking} className={`px-9 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-3 cursor-pointer`} style={{ backgroundColor: '#fff', color: t.primary }}>
              <Calendar className="w-4 h-4" /> {cp.bookLabel} <ArrowRight className="w-4 h-4" />
            </button>
            {c.phone && <a href={`tel:${c.phone}`} className={`px-7 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-2 border`} style={{ borderColor: withAlpha('#fff', 0.5), color: '#fff' }}><Phone className="w-4 h-4" />{c.phone}</a>}
          </div>
        </div>
      </Reveal>
    </section>
  );
}

function MinimalQuote() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <Reveal>
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-3xl sm:text-4xl leading-snug mb-8 italic" style={{ fontFamily: t.serifFamily, color: t.text }}>
            “The best time to take the first step was yesterday. The second best time is today.”
          </p>
          <button onClick={openBooking} className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-wider pb-1 cursor-pointer" style={{ color: t.accent, borderBottom: `2px solid ${t.accent}` }}>
            {cp.bookLabel} with {c.name} <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </Reveal>
    </Section>
  );
}

function CardFloating() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <Reveal>
        <div className={`max-w-4xl mx-auto p-10 sm:p-14 ${t.cardRadius} text-center relative`}
          style={{ backgroundColor: t.surface, border: `1px solid ${t.border}`, boxShadow: `0 40px 80px ${withAlpha(t.primary, t.isDark ? 0.35 : 0.15)}` }}>
          <div className="w-16 h-16 rounded-2xl mx-auto mb-6 flex items-center justify-center" style={{ background: t.primaryGradient }}><Calendar className="w-7 h-7 text-white" /></div>
          <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ fontFamily: t.serifFamily, color: t.text }}>Let&apos;s get started</h2>
          <p className="text-base max-w-lg mx-auto mb-8 leading-relaxed" style={{ color: t.subtext }}>Straightforward, transparent, and tailored to you — that&apos;s the service at {c.name}.</p>
          <PrimaryButton onClick={openBooking}>{cp.bookLabel}</PrimaryButton>
        </div>
      </Reveal>
    </Section>
  );
}

function PhonePrimary() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <Reveal>
        <div className="max-w-3xl mx-auto text-center">
          <span className="text-xs font-bold uppercase tracking-widest" style={{ color: t.accent }}>Speak to our team now</span>
          <a href={c.phone ? `tel:${c.phone}` : '#'} className="block text-5xl sm:text-7xl font-extrabold my-6 tracking-tight" style={{ fontFamily: t.serifFamily, color: t.text }}>{c.phone || 'Call Today'}</a>
          <p className="text-base mb-8" style={{ color: t.subtext }}>Friendly, responsive service for {cp.audience} in {c.city}.</p>
          <PrimaryButton onClick={openBooking}>Or Enquire Online</PrimaryButton>
        </div>
      </Reveal>
    </Section>
  );
}

function BentoFinale() {
  const { c, t, openBooking, cp } = useCta();
  return (
    <Section>
      <div className="grid md:grid-cols-3 gap-5">
        <Reveal className="md:col-span-2">
          <div className={`h-full p-10 ${t.cardRadius} border flex flex-col justify-between`}
            style={{ borderColor: t.border, background: `linear-gradient(150deg, ${withAlpha(t.primary, t.isDark ? 0.3 : 0.1)}, ${t.surface})` }}>
            <h2 className="text-3xl sm:text-5xl font-bold mb-6" style={{ fontFamily: t.serifFamily, color: t.text }}>Get in touch with {c.name}</h2>
            <PrimaryButton onClick={openBooking}>{cp.bookLabel}</PrimaryButton>
          </div>
        </Reveal>
        <div className="grid gap-5">
          <Reveal delay={0.05}>
            <div className={`p-7 ${t.cardRadius} border text-center`} style={{ borderColor: t.border, backgroundColor: t.surface }}>
              <div className="flex justify-center mb-2"><Stars /></div>
              <div className="text-3xl font-extrabold" style={{ fontFamily: t.serifFamily, color: t.accent }}>{c.google_rating}</div>
              <div className="text-[11px] uppercase tracking-widest font-bold" style={{ color: t.subtext }}>{c.review_count}+ reviews</div>
            </div>
          </Reveal>
          {c.phone && (
            <Reveal delay={0.1}>
              <a href={`tel:${c.phone}`} className={`p-7 ${t.cardRadius} border flex items-center gap-3`} style={{ borderColor: t.border, backgroundColor: t.surface }}>
                <Phone className="w-5 h-5" style={{ color: t.accent }} /><span className="font-bold" style={{ color: t.text }}>{c.phone}</span>
              </a>
            </Reveal>
          )}
        </div>
      </div>
    </Section>
  );
}

const MAP: Record<string, React.FC> = {
  CTA_RADIAL_GLOW_BANNER: RadialGlow,
  CTA_DARK_OBSIDIAN: RadialGlow,
  CTA_SPLIT_APPOINTMENT: SplitAppointment,
  CTA_STICKY_BOTTOM_BAR: SplitAppointment,
  CTA_FULL_WIDTH_GRADIENT: FullWidthGradient,
  CTA_WARM_WELLNESS: CardFloating,
  CTA_CARD_FLOATING: CardFloating,
  CTA_MINIMAL_QUOTE: MinimalQuote,
  CTA_PHONE_PRIMARY: PhonePrimary,
  CTA_BENTO_FINALE: BentoFinale,
};

export default function Cta() {
  const { config } = useSite();
  const v = config.layout_tree?.variants?.cta || 'CTA_RADIAL_GLOW_BANNER';
  const Cmp = MAP[v] || RadialGlow;
  return <Cmp />;
}
