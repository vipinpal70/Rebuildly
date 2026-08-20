'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Phone, Clock, Navigation, BadgeCheck, Camera, Users } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, Stagger, StaggerItem, SectionHeading, Section, Card, PrimaryButton } from '../site/ui';

/* ================================ GALLERY ================================= */
export function Gallery() {
  const { config: c, theme: t } = useSite();
  const shots = c.gallery || [];
  if (!shots.length) return null;
  // Editorial mosaic: first tile spans 2 columns + 2 rows.
  return (
    <Section id="gallery">
      <Reveal>
        <SectionHeading eyebrow="Inside the practice" icon={<Camera className="w-4 h-4" />} title="A Look" accent="Inside"
          subtitle={`Modern, calming, and spotlessly clean — this is where your care happens in ${c.city}.`} />
      </Reveal>
      <div className="grid grid-cols-2 lg:grid-cols-4 auto-rows-[180px] sm:auto-rows-[220px] gap-4">
        {shots.map((g: any, i: number) => (
          <Reveal key={i} delay={(i % 4) * 0.06} className={i === 0 ? 'col-span-2 row-span-2' : ''}>
            <motion.div
              whileHover={{ scale: 0.985 }}
              className={`group relative w-full h-full overflow-hidden ${t.cardRadius}`}
              style={{ border: `1px solid ${t.border}` }}
            >
              <img src={g.src} alt={g.caption} loading="lazy" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 flex items-end p-4 opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ background: `linear-gradient(to top, ${t.scrim(0.85)}, transparent 60%)` }}>
                <span className="text-sm font-semibold" style={{ color: '#fff' }}>{g.caption}</span>
              </div>
            </motion.div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

/* ================================= TEAM =================================== */
export function Team() {
  const { config: c, theme: t } = useSite();
  const team = c.team || [];
  if (!team.length) return null;
  return (
    <Section id="team" tint>
      <Reveal>
        <SectionHeading eyebrow="Meet the team" icon={<Users className="w-4 h-4" />} title="The People Behind" accent={c.name}
          subtitle={`Experienced, friendly, and genuinely invested in your outcome.`} />
      </Reveal>
      <Stagger className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {team.map((m: any, i: number) => (
          <StaggerItem key={i}>
            <Card className="overflow-hidden h-full flex flex-col">
              <div className="relative h-64 overflow-hidden">
                <img src={m.photo} alt={m.name} loading="lazy" className="w-full h-full object-cover transition-transform duration-700 hover:scale-105" />
                <div className="absolute inset-x-0 bottom-0 h-24" style={{ background: `linear-gradient(to top, ${t.surfaceSolid}, transparent)` }} />
              </div>
              <div className="p-6 pt-3 flex-1 flex flex-col">
                <h3 className="text-lg font-bold" style={{ fontFamily: t.serifFamily, color: t.text }}>{m.name}</h3>
                {m.role && <div className="text-xs font-semibold mb-2" style={{ color: t.accent }}>{m.role}</div>}
                {m.credentials && (
                  <div className="inline-flex items-center gap-1.5 text-[11px] mb-3" style={{ color: t.subtext }}>
                    <BadgeCheck className="w-3.5 h-3.5" style={{ color: t.accent }} />{m.credentials}
                  </div>
                )}
                <p className="text-xs leading-relaxed" style={{ color: t.subtext }}>{m.bio}</p>
              </div>
            </Card>
          </StaggerItem>
        ))}
      </Stagger>
    </Section>
  );
}

/* =============================== LOCATION ================================= */
export function LocationMap() {
  const { config: c, theme: t } = useSite();
  const hours = c.hours || [];
  const today = new Date().toLocaleDateString('en-GB', { weekday: 'long' });
  const mapUrl = c.map_embed_url || `https://www.google.com/maps?q=${encodeURIComponent(c.address || `${c.name}, ${c.city}`)}&output=embed`;
  return (
    <Section id="location">
      <Reveal>
        <SectionHeading eyebrow="Find us" icon={<MapPin className="w-4 h-4" />} title="Visit Us in" accent={c.city} center={false}
          subtitle="Easy to reach, with free parking and step-free access." />
      </Reveal>
      <div className="grid lg:grid-cols-2 gap-8">
        <Reveal>
          <div className="space-y-4">
            <Card hover={false} className="p-6 flex items-start gap-4">
              <span className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ background: t.primaryGradient }}><MapPin className="w-5 h-5 text-white" /></span>
              <div>
                <div className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: t.subtext }}>Address</div>
                <div className="text-sm font-medium" style={{ color: t.text }}>{c.address || `${c.city}, ${c.country}`}</div>
                {c.google_maps_url && (
                  <a href={c.google_maps_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-xs font-bold mt-2" style={{ color: t.accent }}>
                    <Navigation className="w-3.5 h-3.5" /> Get directions
                  </a>
                )}
              </div>
            </Card>

            {c.phone && (
              <Card hover={false} className="p-6 flex items-start gap-4">
                <span className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ background: t.primaryGradient }}><Phone className="w-5 h-5 text-white" /></span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider mb-1" style={{ color: t.subtext }}>Call us</div>
                  <a href={`tel:${c.phone}`} className="text-lg font-bold" style={{ color: t.text }}>{c.phone}</a>
                </div>
              </Card>
            )}

            {hours.length > 0 && (
            <Card hover={false} className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ background: t.primaryGradient }}><Clock className="w-5 h-5 text-white" /></span>
                <div className="text-xs font-bold uppercase tracking-wider" style={{ color: t.subtext }}>Opening hours</div>
              </div>
              <ul className="space-y-1.5">
                {hours.map((h: any, i: number) => {
                  const isToday = h.day === today;
                  return (
                    <li key={i} className="flex items-center justify-between text-sm py-1.5 px-2 rounded-lg"
                      style={{ backgroundColor: isToday ? t.badgeBg : 'transparent', color: isToday ? t.text : t.subtext }}>
                      <span className="font-medium flex items-center gap-2">{isToday && <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: '#34d399' }} />}{h.day}</span>
                      <span style={{ color: isToday ? t.accent : t.subtext, fontWeight: isToday ? 700 : 400 }}>{h.time}</span>
                    </li>
                  );
                })}
              </ul>
            </Card>
            )}
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className={`h-full min-h-[420px] overflow-hidden ${t.cardRadius}`} style={{ border: `1px solid ${t.border}` }}>
            <iframe
              title={`Map to ${c.name}`}
              src={mapUrl}
              className="w-full h-full"
              style={{ border: 0, minHeight: 420, filter: t.isDark ? 'invert(0.92) hue-rotate(180deg) contrast(0.9)' : 'none' }}
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              allowFullScreen
            />
          </div>
        </Reveal>
      </div>
    </Section>
  );
}
