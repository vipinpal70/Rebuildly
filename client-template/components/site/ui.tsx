'use client';

import React, { useRef } from 'react';
import { motion, useReducedMotion, useMotionValue, useSpring } from 'framer-motion';
import { Star, ArrowRight, Calendar } from 'lucide-react';
import { fadeUp, staggerParent, staggerChild, springHover, springMagnetic, wordReveal, wordRevealParent, splitWords } from './motion';
import { useSite } from './SiteProvider';
import { withAlpha } from './theme';

/** Cursor-follow "magnetic" offset — the element eases toward the pointer within a
 * capped radius, then springs back on leave. A common premium-agency-site button
 * micro-interaction; disabled under prefers-reduced-motion. */
function useMagnetic(strength = 0.35, max = 14) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, springMagnetic);
  const springY = useSpring(y, springMagnetic);

  const onMouseMove = (e: React.MouseEvent) => {
    if (reduce || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const relX = e.clientX - (rect.left + rect.width / 2);
    const relY = e.clientY - (rect.top + rect.height / 2);
    x.set(Math.max(-max, Math.min(max, relX * strength)));
    y.set(Math.max(-max, Math.min(max, relY * strength)));
  };
  const onMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return { ref, style: { x: springX, y: springY }, onMouseMove, onMouseLeave };
}

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
  const mag = useMagnetic();
  return (
    <motion.button
      ref={mag.ref as any}
      onClick={onClick}
      onMouseMove={mag.onMouseMove}
      onMouseLeave={mag.onMouseLeave}
      style={{ ...mag.style, background: t.primaryGradient, color: '#fff', boxShadow: `0 14px 40px ${t.glow(0.35)}` }}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.97 }}
      transition={springHover}
      className={`group ${full ? 'w-full justify-center' : ''} px-5 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-3 cursor-pointer ${className}`}
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
  const mag = useMagnetic();
  const cls = `px-5 py-4 ${t.btnRadius} text-sm font-bold uppercase tracking-wider inline-flex items-center gap-2 transition-colors ${className}`;
  const style: any = {
    ...mag.style,
    border: `1px solid ${t.border}`,
    color: t.text,
    background: withAlpha(t.text, 0.03),
  };
  if (href) return (
    <motion.a ref={mag.ref as any} href={href} onMouseMove={mag.onMouseMove} onMouseLeave={mag.onMouseLeave} className={cls} style={style}>
      {children}
    </motion.a>
  );
  return (
    <motion.button ref={mag.ref as any} onClick={onClick} onMouseMove={mag.onMouseMove} onMouseLeave={mag.onMouseLeave} className={cls} style={style}>
      {children}
    </motion.button>
  );
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
    <div className={`${center ? 'text-center mx-auto' : ''} max-w-3xl mb-8`}>
      {eyebrow && <Eyebrow icon={icon}>{eyebrow}</Eyebrow>}
      <h2 className="text-xl sm:text-3xl font-bold tracking-tight leading-[1.1]" style={{ fontFamily: t.serifFamily, color: t.text }}>
        {title}{' '}
        {accent && <span style={{ color: t.accent, fontStyle: t.isEditorial ? 'italic' : 'normal' }}>{accent}</span>}
        {tail ? ` ${tail}` : ''}
      </h2>
      {subtitle && <p className="mt-5 text-sm leading-relaxed" style={{ color: t.subtext }}>{subtitle}</p>}
    </div>
  );
}

/** Word-by-word clip-reveal for display headlines (hero H1s, big section quotes).
 * Each word sits in its own overflow-hidden mask and rises into view on its own
 * beat, rather than the whole line fading in as one flat block — the difference
 * between a template scroll-reveal and something that reads as actually designed.
 * Falls back to plain static text under prefers-reduced-motion. */
export function TextReveal({
  text,
  delay = 0,
  stagger = 0.05,
  as: Tag = 'span',
  className = '',
}: {
  text: string;
  delay?: number;
  stagger?: number;
  as?: 'span' | 'div';
  className?: string;
}) {
  const reduce = useReducedMotion();
  if (reduce) return <Tag className={className}>{text}</Tag>;
  const words = splitWords(text);
  return (
    <motion.span
      className={`inline ${className}`}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-80px' }}
      variants={wordRevealParent(stagger, delay)}
      aria-label={text}
    >
      {words.map((w, i) => (
        <span key={i} className="inline-block overflow-hidden align-bottom" aria-hidden>
          <motion.span className="inline-block" variants={wordReveal}>
            {w}
            {i < words.length - 1 ? ' ' : ''}
          </motion.span>
        </span>
      ))}
    </motion.span>
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

// A soft multi-stop mesh + fine grid that reads correctly on light AND dark. The
// two colour blobs drift slowly and continuously — barely perceptible frame to
// frame, but it's the difference between a backdrop that feels alive and one
// that's just a static image; disabled under prefers-reduced-motion.
export function MeshBackdrop({ grid = true }: { grid?: boolean }) {
  const { theme: t } = useSite();
  const reduce = useReducedMotion();
  return (
    <div aria-hidden className="absolute inset-0 pointer-events-none overflow-hidden">
      <motion.div
        className="absolute inset-0"
        style={{
          background: `radial-gradient(60% 55% at 15% 0%, ${withAlpha(t.primary, t.isDark ? 0.18 : 0.10)}, transparent 60%),
                       radial-gradient(50% 50% at 90% 20%, ${withAlpha(t.accent, t.isDark ? 0.16 : 0.09)}, transparent 55%)`,
        }}
        animate={reduce ? undefined : {
          backgroundPosition: ['0% 0%, 0% 0%', '4% 3%, -3% 4%', '0% 0%, 0% 0%'],
        }}
        transition={reduce ? undefined : { duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
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
      className={`relative py-10 sm:py-12 px-4 sm:px-5 ${className}`}
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
  spotlight = true,
  style = {},
}: {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  /** Soft radial glow that tracks the cursor within the card — a common premium
   * SaaS-site micro-interaction. Set via direct style writes on mousemove (not
   * React state) so it stays smooth without a re-render per pixel of movement. */
  spotlight?: boolean;
  style?: React.CSSProperties;
}) {
  const { theme: t } = useSite();
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const showSpotlight = spotlight && hover && !reduce;

  const onMouseMove = showSpotlight
    ? (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = ref.current?.getBoundingClientRect();
        if (!rect) return;
        ref.current!.style.setProperty('--mx', `${e.clientX - rect.left}px`);
        ref.current!.style.setProperty('--my', `${e.clientY - rect.top}px`);
        ref.current!.style.setProperty('--mo', '1');
      }
    : undefined;
  const onMouseLeave = showSpotlight ? () => ref.current?.style.setProperty('--mo', '0') : undefined;

  return (
    <div
      ref={ref}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      className={`relative ${t.cardRadius} border ${showSpotlight ? 'overflow-hidden' : ''} ${hover ? 'transition-all duration-300 hover:-translate-y-1.5' : ''} ${className}`}
      style={{
        backgroundColor: t.surface,
        borderColor: t.border,
        backdropFilter: t.isDark ? 'blur(16px)' : undefined,
        boxShadow: t.isDark ? undefined : '0 1px 2px rgba(15,23,42,0.04), 0 12px 32px rgba(15,23,42,0.06)',
        ...style,
      }}
    >
      {/* Absolutely positioned, so it's excluded from flex/grid layout — callers
          that use Card as a direct flex/grid container of `children` (e.g.
          `flex flex-col justify-between`) are unaffected; children stay direct
          children of the root rather than being wrapped in an extra element. */}
      {showSpotlight && (
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300"
          style={{
            opacity: 'var(--mo, 0)',
            background: `radial-gradient(240px circle at var(--mx, 50%) var(--my, 50%), ${withAlpha(t.accent, t.isDark ? 0.14 : 0.08)}, transparent 70%)`,
          }}
        />
      )}
      {children}
    </div>
  );
}
