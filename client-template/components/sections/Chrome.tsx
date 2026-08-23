'use client';

import React, { useState } from 'react';
import { motion, useScroll, useMotionValueEvent } from 'framer-motion';
import { Phone, MapPin, Calendar, Menu, X } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { siteCopy } from '../site/copy';

const NAV = [
  { href: '#services', label: 'Services' },
  { href: '#why-us', label: 'Why Us' },
  { href: '#workflow', label: 'Process' },
  { href: '#reviews', label: 'Reviews' },
  { href: '#faq', label: 'FAQ' },
];

export function TopStrip() {
  const { config: c, theme: t, openBooking } = useSite();
  return (
    <div className="text-xs py-2.5 px-4 sm:px-5" style={{ backgroundColor: withAlpha(t.isDark ? '#000' : t.primary, t.isDark ? 0.3 : 0.04), color: t.subtext, borderBottom: `1px solid ${t.hairline}` }}>
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" style={{ color: t.accent }} />{c.city}, {c.country}</span>
          {c.phone && <a href={`tel:${c.phone}`} className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5" style={{ color: t.accent }} />{c.phone}</a>}
        </div>
        {c.google_rating && (
          <span className="hidden sm:inline-flex items-center gap-1.5 font-semibold" style={{ color: t.text }}>
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#34d399' }} /> Rated {c.google_rating}★ by {c.review_count}+ {siteCopy(c).audience}
          </span>
        )}
      </div>
    </div>
  );
}

export function Header() {
  const { config: c, theme: t, openBooking } = useSite();
  const { scrollY } = useScroll();
  const [shrink, setShrink] = useState(false);
  const [menu, setMenu] = useState(false);
  useMotionValueEvent(scrollY, 'change', (y) => setShrink(y > 40));

  return (
    <motion.header
      className="sticky top-0 z-50 backdrop-blur-2xl"
      style={{ backgroundColor: withAlpha(t.bg, 0.85), borderBottom: `1px solid ${t.hairline}` }}
      animate={{ height: shrink ? 64 : 80 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-5 h-full flex items-center justify-between">
        <a href="#" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-base shadow-lg" style={{ background: t.primaryGradient, color: '#fff', fontFamily: t.serifFamily }}>
            {c.name?.charAt(0)}
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base tracking-tight leading-none" style={{ fontFamily: t.serifFamily, color: t.text }}>{c.name}</span>
            <span className="text-[11px] font-medium tracking-wide uppercase" style={{ color: t.subtext }}>{c.category} · {c.city}</span>
          </div>
        </a>

        <nav className="hidden md:flex items-center gap-5 text-sm font-medium" style={{ color: t.text }}>
          {NAV.map((n) => <a key={n.href} href={n.href} className="hover:opacity-70 transition-opacity">{n.label}</a>)}
        </nav>

        <div className="hidden lg:flex items-center gap-3">
          {c.phone && (
            <a href={`tel:${c.phone}`} className="w-10 h-10 rounded-xl flex items-center justify-center border transition-colors" style={{ borderColor: t.border, color: t.accent }} aria-label="Call">
              <Phone className="w-4 h-4" />
            </a>
          )}
          <button onClick={openBooking} className={`px-5 py-2.5 text-xs font-bold text-white uppercase tracking-wider cursor-pointer ${t.btnRadius} inline-flex items-center gap-1.5`} style={{ background: t.primaryGradient, boxShadow: `0 8px 24px ${t.glow(0.3)}` }}>
            <Calendar className="w-4 h-4" /> {siteCopy(c).bookLabel}
          </button>
        </div>

        <button className="md:hidden p-2" onClick={() => setMenu(!menu)} style={{ color: t.text }} aria-label="Menu">
          {menu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {menu && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="md:hidden px-4 pb-5 pt-2 space-y-1" style={{ backgroundColor: t.bg, borderBottom: `1px solid ${t.hairline}` }}>
          {NAV.map((n) => <a key={n.href} href={n.href} onClick={() => setMenu(false)} className="block py-2.5 text-sm font-medium" style={{ color: t.text }}>{n.label}</a>)}
          <button onClick={() => { setMenu(false); openBooking(); }} className={`w-full mt-2 py-3 text-xs font-bold text-white uppercase tracking-wider ${t.btnRadius}`} style={{ background: t.primaryGradient }}>{siteCopy(c).bookLabel}</button>
        </motion.div>
      )}
    </motion.header>
  );
}

export function Footer() {
  const { config: c, theme: t } = useSite();
  return (
    <footer className="py-8 px-4 text-center text-xs" style={{ color: t.subtext, borderTop: `1px solid ${t.hairline}` }}>
      <div className="max-w-7xl mx-auto space-y-3">
        <p className="font-semibold text-sm" style={{ color: t.text, fontFamily: t.serifFamily }}>{c.name}</p>
        <p>{c.address ? `${c.address}, ` : ''}{c.city}, {c.country}</p>
        {c.phone && <p><a href={`tel:${c.phone}`} style={{ color: t.accent }}>{c.phone}</a></p>}
        <p className="pt-2 opacity-70">© {new Date().getFullYear()} {c.name}. All rights reserved. · Crafted with care.</p>
      </div>
    </footer>
  );
}
