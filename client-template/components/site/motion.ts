// Shared framer-motion presets. Centralised so timing/feel is consistent across
// every section and easy to tune in one place. All reveals respect
// `prefers-reduced-motion` via the <Reveal> primitive.

import type { Variants } from 'framer-motion';

export const EASE_OUT = [0.16, 1, 0.3, 1] as const;

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 28 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: EASE_OUT } },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.8, ease: EASE_OUT } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.94 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.6, ease: EASE_OUT } },
};

// Parent container that staggers its direct children (use with `fadeUp`).
export const staggerParent = (stagger = 0.09, delay = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: stagger, delayChildren: delay } },
});

export const staggerChild: Variants = {
  hidden: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EASE_OUT } },
};

// Spring physics for interactive buttons / cards.
export const springHover = { type: 'spring', stiffness: 400, damping: 22 } as const;
