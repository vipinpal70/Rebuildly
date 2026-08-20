'use client';

import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Star, ArrowRight, Calendar } from 'lucide-react';
import { fadeUp, staggerParent, staggerChild, springHover } from './motion';
import { useSite } from './SiteProvider';
import { withAlpha } from './theme';

/* ---------------------------------- motion --------------------------------- */

export function Reveal({
  children,
  delay = 0,
  y = 28,
  className,
  as = 'div',
}: {
  children: React.ReactNode;
  delay?: number;
  y?: number;
  className?: string;
  as?: 'div' | 'section' | 'span' | 'li';
}) {
  const reduce = useReducedMotion();
  const Comp: any = (motion as any)[as] || motion.div;
  if (reduce) {
    const Plain: any = as;
    return <Plain className={className}>{children}</Plain>;
  }
  return (
    <Comp
      className={className}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-60px' }}
      variants={{
        hidden: { opacity: 0, y },
        show: { opacity: 1, y: 0, transition: { duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] } },
      }}
    >
      {children}
    </Comp>
  );
}

export function Stagger({
  children,
  className,
  stagger = 0.09,
}: {
  children: React.ReactNode;
  className?: string;
  stagger?: number;
}) {
  const reduce = useReducedMotion();
  if (reduce) return <div className={className}>{children}</div>;
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-60px' }}
      variants={staggerParent(stagger)}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className }: { children: React.ReactNode; className?: string }) {
  const reduce = useReducedMotion();
  if (reduce) return <div className={className}>{children}</div>;
  return (
    <motion.div className={className} variants={staggerChild}>
      {children}
    </motion.div>
  );
}

/* --------------------------------- buttons --------------------------------- */

export function PrimaryButton({
  children,
  onClick,
  icon = true,
  className = '',
  full = false,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  icon?: boolean;
  className?: string;
  full?: boolean;
}) {
  const { theme: t } = useSite();
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.97 }}
      transition={springHover}
      className={`group ${full ? 'w-full justify-center' : ''} px-8 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-3 cursor-pointer ${className}`}
      style={{ background: t.primaryGradient, color: '#fff', boxShadow: `0 14px 40px ${t.glow(0.35)}` }}
    >
      {icon && <Calendar className="w-4 h-4" />}
      <span>{children}</span>
      {icon && <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />}
    </motion.button>
  );
}

export function GhostButton({
  children,
  onClick,
  href,
  className = '',
}: {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  className?: string;
}) {
  const { theme: t } = useSite();
  const cls = `px-7 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-2 transition-colors ${className}`;
  const style: React.CSSProperties = {
    border: `1px solid ${t.border}`,
    color: t.text,
    background: withAlpha(t.text, 0.03),
  };
  if (href) return <a href={href} className={cls} style={style}>{children}</a>;
  return <button onClick={onClick} className={cls} style={style}>{children}</button>;
}

/* ---------------------------------- chrome --------------------------------- */

export function LiveBadge({ label }: { label: string }) {
  const { theme: t } = useSite();
  return (
    <div
      className={`inline-flex items-center gap-2.5 px-4 py-2 ${t.btnRadius} text-[11px] font-bold tracking-widest uppercase border backdrop-blur-xl`}
      style={{ backgroundColor: t.badgeBg, color: t.badgeText, borderColor: t.border }}
    >
      <span className="relative flex h-2.5 w-2.5">
        <span className="absolute inline-flex h-full w-full rounded-full opacity-70 animate-ping" style={{ backgroundColor: '#34d399' }} />
        <span className="relative inline-flex rounded-full h-2.5 w-2.5" style={{ backgroundColor: '#34d399' }} />
      </span>
      <span>{label}</span>
    </div>
  );
}

export function Eyebrow({ children, icon }: { children: React.ReactNode; icon?: React.ReactNode }) {
  const { theme: t } = useSite();
  return (
    <div className="inline-flex items-center gap-2 text-xs font-bold tracking-[0.2em] uppercase mb-4" style={{ color: t.accent }}>
      {icon}
      <span>{children}</span>
    </div>
  );
}

export function SectionHeading({
  eyebrow,
  icon,
  title,
  accent,
  tail,
  subtitle,
  center = true,
}: {
  eyebrow?: string;
  icon?: React.ReactNode;
  title: string;
  accent?: string;
  tail?: string;
  subtitle?: string;
  center?: boolean;
}) {
  const { theme: t } = useSite();
  return (
    <div className={`${center ? 'text-center mx-auto' : ''} max-w-3xl mb-14`}>
      {eyebrow && <Eyebrow icon={icon}>{eyebrow}</Eyebrow>}
      <h2 className="text-3xl sm:text-5xl font-bold tracking-tight leading-[1.1]" style={{ fontFamily: t.serifFamily, color: t.text }}>
        {title}{' '}
        {accent && <span style={{ color: t.accent, fontStyle: t.isEditorial ? 'italic' : 'normal' }}>{accent}</span>}
        {tail ? ` ${tail}` : ''}
      </h2>
      {subtitle && <p className="mt-5 text-sm sm:text-base leading-relaxed" style={{ color: t.subtext }}>{subtitle}</p>}
    </div>
  );
}

/* --------------------------------- effects --------------------------------- */

export function AmbientGlow({
  className = '',
  size = 500,
  color,
  alpha = 0.16,
}: {
  className?: string;
  size?: number;
  color?: string;
  alpha?: number;
}) {
  const { theme: t } = useSite();
  return (
    <div
      aria-hidden
      className={`absolute rounded-full pointer-events-none blur-[130px] ${className}`}
      style={{ width: size, height: size, backgroundColor: color || withAlpha(t.accent, alpha) }}
    />
  );
}

// A soft multi-stop mesh + fine grid that reads correctly on light AND dark.
export function MeshBackdrop({ grid = true }: { grid?: boolean }) {
  const { theme: t } = useSite();
  return (
    <div aria-hidden className="absolute inset-0 pointer-events-none overflow-hidden">
      <div className="absolute inset-0" style={{
        background: `radial-gradient(60% 55% at 15% 0%, ${withAlpha(t.primary, t.isDark ? 0.18 : 0.10)}, transparent 60%),
                     radial-gradient(50% 50% at 90% 20%, ${withAlpha(t.accent, t.isDark ? 0.16 : 0.09)}, transparent 55%)`,
      }} />
      {grid && (
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, ${withAlpha(t.text, t.isDark ? 0.06 : 0.05)} 1px, transparent 0)`,
          backgroundSize: '38px 38px',
          maskImage: 'radial-gradient(ellipse 80% 60% at 50% 0%, black, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 60% at 50% 0%, black, transparent 75%)',
        }} />
      )}
    </div>
  );
}

/* ---------------------------------- atoms ---------------------------------- */

export function Stars({ n = 5, className = 'w-4 h-4' }: { n?: number; className?: string }) {
  return (
    <div className="flex gap-0.5" style={{ color: '#f59e0b' }}>
      {Array.from({ length: n }).map((_, i) => (
        <Star key={i} className={className} style={{ fill: '#f59e0b' }} />
      ))}
    </div>
  );
}

export function Avatar({ letter, i = 0 }: { letter: string; i?: number }) {
  const { theme: t } = useSite();
  const tints = [t.primary, t.accent, t.primaryHover];
  return (
    <div
      className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-white text-xs shadow-lg"
      style={{ backgroundColor: tints[i % tints.length] }}
    >
      {letter}
    </div>
  );
}

// Section wrapper: consistent rhythm + optional tinted band that adapts to theme.
export function Section({
  children,
  id,
  tint = false,
  className = '',
}: {
  children: React.ReactNode;
  id?: string;
  tint?: boolean;
  className?: string;
}) {
  const { theme: t } = useSite();
  return (
    <section
      id={id}
      className={`relative py-20 sm:py-28 px-4 sm:px-8 ${className}`}
      style={{
        borderTop: `1px solid ${t.hairline}`,
        backgroundColor: tint ? withAlpha(t.isDark ? '#000000' : t.primary, t.isDark ? 0.22 : 0.03) : 'transparent',
      }}
    >
      <div className="max-w-7xl mx-auto relative z-10">{children}</div>
    </section>
  );
}

export function Card({
  children,
  className = '',
  hover = true,
  style = {},
}: {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  style?: React.CSSProperties;
}) {
  const { theme: t } = useSite();
  return (
    <div
      className={`${t.cardRadius} border ${hover ? 'transition-all duration-300 hover:-translate-y-1.5' : ''} ${className}`}
      style={{
        backgroundColor: t.surface,
        borderColor: t.border,
        backdropFilter: t.isDark ? 'blur(16px)' : undefined,
        boxShadow: t.isDark ? undefined : '0 1px 2px rgba(15,23,42,0.04), 0 12px 32px rgba(15,23,42,0.06)',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
