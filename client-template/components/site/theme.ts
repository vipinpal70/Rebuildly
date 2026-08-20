// Derives a full, palette-aware theme from the generator's `colors` payload.
// Every section reads from this so a site NEVER hardcodes a colour again —
// the same component renders correctly on a dark obsidian palette and a light
// parchment one.

export interface RawColors {
  name?: string;
  archetype?: string;
  bg?: string;
  surface?: string;
  text?: string;
  subtext?: string;
  primary?: string;
  primary_hover?: string;
  accent?: string;
  border?: string;
  badge_bg?: string;
  badge_text?: string;
  heading_font?: string;
  body_font?: string;
}

export interface Theme {
  archetype: string;
  isDark: boolean;
  bg: string;
  surface: string;
  surfaceSolid: string;
  text: string;
  subtext: string;
  primary: string;
  primaryHover: string;
  accent: string;
  border: string;
  hairline: string;
  badgeBg: string;
  badgeText: string;
  headingFont: string;
  bodyFont: string;
  cardRadius: string;
  btnRadius: string;
  // derived helpers
  primaryGradient: string;
  glow: (alpha?: number) => string;
  accentSoft: string;
  scrim: (alpha?: number) => string;   // rgba of the page bg — for image overlays
  onImage: string;                      // text colour guaranteed readable on media
  onImageSoft: string;
  serifFamily: string;                  // heading font-family string
  sansFamily: string;                   // body font-family string
  isTech: boolean;                      // cyber / tech archetypes → code motifs
  isEditorial: boolean;                 // heritage / editorial → serif, calm
}

function parseColor(input?: string): { r: number; g: number; b: number } | null {
  if (!input) return null;
  const s = input.trim();
  const hex = s.replace('#', '');
  if (/^[0-9a-fA-F]{3}$/.test(hex)) {
    return {
      r: parseInt(hex[0] + hex[0], 16),
      g: parseInt(hex[1] + hex[1], 16),
      b: parseInt(hex[2] + hex[2], 16),
    };
  }
  if (/^[0-9a-fA-F]{6}$/.test(hex)) {
    return {
      r: parseInt(hex.slice(0, 2), 16),
      g: parseInt(hex.slice(2, 4), 16),
      b: parseInt(hex.slice(4, 6), 16),
    };
  }
  const m = s.match(/rgba?\(([^)]+)\)/);
  if (m) {
    const [r, g, b] = m[1].split(',').map((v) => parseFloat(v));
    return { r, g, b };
  }
  return null;
}

function relativeLuminance(c: { r: number; g: number; b: number }): number {
  const lin = (v: number) => {
    const x = v / 255;
    return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
}

export function withAlpha(color: string | undefined, alpha: number): string {
  const c = parseColor(color);
  if (!c) return `rgba(0,0,0,${alpha})`;
  return `rgba(${c.r}, ${c.g}, ${c.b}, ${alpha})`;
}

const TECH = new Set(['CYBER_GLOW_TECH', 'NEO_BRUTALIST_VIBRANT']);
const EDITORIAL = new Set(['EDITORIAL_ELEGANCE', 'WARM_ORGANIC_WELLNESS', 'CORPORATE_HIGH_TRUST']);

export function buildTheme(colors: RawColors = {}, cardRadius?: string, btnRadius?: string): Theme {
  const bg = colors.bg || '#07101f';
  const bgRgb = parseColor(bg);
  const isDark = bgRgb ? relativeLuminance(bgRgb) < 0.45 : true;

  const text = colors.text || (isDark ? '#f8fafc' : '#0f172a');
  const subtext = colors.subtext || (isDark ? '#94a3b8' : '#475569');
  const accent = colors.accent || '#00b4d8';
  const primary = colors.primary || '#1e56d9';
  const primaryHover = colors.primary_hover || primary;
  const border = colors.border || (isDark ? 'rgba(255,255,255,0.10)' : 'rgba(15,23,42,0.10)');
  const archetype = colors.archetype || 'LUXURY_GLASSMORPHISM';
  const headingFont = colors.heading_font || 'serif';
  const bodyFont = colors.body_font || 'sans-serif';

  return {
    archetype,
    isDark,
    bg,
    surface: colors.surface || (isDark ? 'rgba(255,255,255,0.04)' : '#ffffff'),
    surfaceSolid: isDark ? withAlpha(colors.surface || '#111e35', 0.92) : (colors.surface || '#ffffff'),
    text,
    subtext,
    primary,
    primaryHover,
    accent,
    border,
    hairline: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(15,23,42,0.08)',
    badgeBg: colors.badge_bg || withAlpha(accent, 0.14),
    badgeText: colors.badge_text || accent,
    headingFont,
    bodyFont,
    cardRadius: cardRadius || 'rounded-2xl',
    btnRadius: btnRadius || 'rounded-xl',
    primaryGradient: `linear-gradient(135deg, ${primary}, ${primaryHover})`,
    glow: (a = 0.18) => withAlpha(accent, a),
    accentSoft: withAlpha(accent, 0.12),
    scrim: (a = 0.8) => withAlpha(bg, a),
    onImage: '#ffffff',
    onImageSoft: 'rgba(255,255,255,0.75)',
    serifFamily: `'${headingFont}', Georgia, serif`,
    sansFamily: `'${bodyFont}', system-ui, sans-serif`,
    isTech: TECH.has(archetype),
    isEditorial: EDITORIAL.has(archetype),
  };
}
