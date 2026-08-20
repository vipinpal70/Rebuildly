# ✅ Solution: Making Client Sites Feel Human-Crafted (`client-template-solution.md`)

This is a response to `client-template-issue.md`, grounded in the **actual code** rather than the issue's abstract wishlist. I read the real generator and renderer, cross-checked the generated site data, and found that the true root cause is narrower — and far cheaper to fix — than the issue implies.

---

## 1. The real diagnosis (what I verified in the code)

The issue says sites "feel AI-generated." That symptom is real, but the stated causes are mostly wrong. Here is what is actually happening.

### 1a. The generator promises ~1.4M unique designs. The renderer delivers one.

`src/generator/layout_variants.py` selects, per business (seeded, deterministic):

- **1 of 7 palettes/archetypes** — Glassmorphism, Clinical Minimalist, Warm Ivory, Neo-Brutalist, Corporate High-Trust, Cyber Glow, Editorial Elegance
- **1 of 10 hero variants**, **10 services**, **10 FAQ**, **10 CTA**, **5 reviews**, **4 workflow**, **5 section orders**

That is `7 × 10 × 10 × 10 × 10 × 5 × 4 × 5 ≈ 1.4 million` combinations.

But `client-template/components/DynamicClientSite.tsx` (a single 608-line file) **only reads two of these values**: `variants.hero` (and honors just **1 of the 10** — `HERO_SPLIT_SHOWCASE` — falling back to one "centered luxury" default for the other 9) and `section_order`. Every other selection — `variants.services`, `variants.faq`, `variants.cta`, `variants.reviews`, `variants.workflow` — is **computed, saved to JSON, and then completely ignored** by the renderer. There is exactly one services layout, one FAQ layout, one CTA layout, etc.

**Proof from the actual generated data** (`client-template/public/previews/*.json`):

| Site | Archetype selected | Hero selected | Services selected | CTA selected |
| :-- | :-- | :-- | :-- | :-- |
| clarity-dental-clinic | CYBER_GLOW_TECH | HERO_CYBER_GLOW | SERVICES_HIGHLIGHT_BANNER | CTA_BENTO_FINALE |
| the-redland-road | CLINICAL_MINIMALIST | HERO_COMPACT_BAR | SERVICES_MODERN_PILLS | CTA_RADIAL_GLOW_BANNER |
| john-smith-dental | CORPORATE_HIGH_TRUST | HERO_MINIMAL_EDITORIAL | SERVICES_3COL_CARDS | CTA_DARK_OBSIDIAN |

Every one of those sites renders the **identical** split hero (or the one fallback), the **identical** 3-column services grid, and the **identical** CTA box — because the renderer never branches on those strings. **This is the #1 reason every site looks the same.** It is not a "missing architecture" problem; it is a wiring gap between a rich Python selector and a renderer that throws the selection away.

### 1b. Colors are hardcoded, so 4 of the 7 archetypes are visually broken.

`DynamicClientSite.tsx` hardcodes a dark-cyan aesthetic regardless of the chosen palette. Grep counts in that one file:

- `border-white/10` × 17, `text-white` × 10, `cyan-500` × 7, `cyan-400` × 4, `slate-950/900` × 6
- Plus `hero-grid-bg` (white-dot grid) and cyan spotlight blurs baked into `app/globals.css` with `body { background-color: var(--navy) }`.

For the three **dark** palettes this looks fine. But `CLINICAL_MINIMALIST` (`bg #ffffff`, text `#0f172a`), `WARM_ORGANIC_WELLNESS` (ivory), and `EDITORIAL_ELEGANCE` (parchment) get **white text and white-alpha borders on a white background** — invisible content, a slate-950 image gradient on a light page, cyan icons that clash. So the sites that *are* nominally "different" are actually the *broken* ones. This is issue §1.3, but the fix is "stop hardcoding," not "add noise textures."

### 1c. `framer-motion` and `lucide-react` are installed; `framer-motion` is used in exactly zero files.

`package.json` already has `framer-motion@13` and `lucide-react`. A `grep -rl framer-motion` returns nothing. So issue §1.5 ("integrate Framer Motion") is a real gap, but the dependency is already paid for — it just needs to be used.

### 1d. The interactive widgets the issue calls "missing entirely" already exist.

`components/widgets/` already contains `BeforeAfterSlider.tsx`, `TreatmentCostCalculator.tsx`, and `LiveSlotPicker.tsx`. Two of the three are wired into `renderInteractiveTools()`. So issue §1.2 / the "Missing entirely" rows in the issue's table are **out of date** — `LiveSlotPicker` just isn't mounted yet, and none of the three vary by archetype.

### 1e. Copy fallback is generic, and some sites hit it.

Two generated sites (`john-smith-dental-2e89108d`, `-cdab5919`) have `archetype: null` — they were produced before the layout tree existed or via a path that skipped it, and they render the hardcoded fallback strings from `site_generator.py` ("Exceptional {category} Care in {city}", "Specialized Treatments & Procedures", "Your Care Journey"). That's issue §1.4, and it's a genuine but secondary prompt-quality problem.

### Summary of the gap between the issue and reality

| Issue claim | Reality in code | Priority |
| :-- | :-- | :-- |
| §1.1 "monolithic renderer → identical DOM" | True, and it's the core bug — but because variants are *ignored*, not merely because it's one file | **P0** |
| §1.2 "interactive widgets missing entirely" | Already built; not archetype-aware, one unmounted | P2 |
| §1.3 "flat color / hardcoded hex" | True — hardcoded colors break light archetypes | **P0** |
| §1.4 "generic copy" | True on the fallback path; prompt is thin | P1 |
| §1.5 "no framer-motion" | Installed, unused | P1 |

---

## 2. How I will solve it

The strategy is **"honor what the engine already decides, then make each decision look distinct"** — highest leverage first. I am *not* starting with a full rewrite into per-archetype folders; that's the right end-state but it's the slowest way to stop sites looking identical. I'll get differentiation live in P0, then refactor toward the clean architecture in P3.

### Phase 0 — Palette-driven theming (fixes 1b; unblocks everything) — ~0.5 day

Nothing looks distinct until light archetypes stop rendering white-on-white. So first:

1. **Introduce CSS custom properties driven by the palette.** In `DynamicClientSite.tsx`'s root `<main>`, set inline CSS vars from `colors`:
   ```tsx
   style={{
     ['--c-bg' as any]: colors.bg,
     ['--c-surface' as any]: colors.surface,
     ['--c-text' as any]: colors.text,
     ['--c-subtext' as any]: colors.subtext,
     ['--c-primary' as any]: colors.primary,
     ['--c-accent' as any]: colors.accent,
     ['--c-border' as any]: colors.border,
   }}
   ```
2. **Replace every hardcoded Tailwind color** (`border-white/10`, `text-white`, `text-cyan-400`, `bg-slate-9xx`, cyan spotlight blurs) with `style` props reading those vars or the existing `colors.*` tokens. Borders → `borderColor: 'var(--c-border)'`; ambient glow → `background: colors.accent` at low opacity instead of a fixed cyan.
3. **Make `globals.css` archetype-neutral.** Remove the `body { background-color: var(--navy) }` default and the `hero-grid-bg` white-dot assumption; drive the grid/glow color from `--c-accent`/`--c-border` so it reads correctly on both light and dark backgrounds.

Deliverable: the same single layout, but now **correct on all 7 palettes**. This alone makes the three "broken" archetypes usable and immediately triples the perceived variety.

### Phase 1 — Wire the variants that are already selected (fixes 1a; the big win) — ~2–3 days

Make the renderer branch on the values the Python engine already emits. I'll refactor each `render*` function into a small switch keyed on the variant string, with each branch being a genuinely different layout.

- **Hero**: implement the remaining 8 of 10 variants as distinct components — `HERO_BENTO_GRID` (asymmetric tiles), `HERO_SIDE_FORM` (embedded booking form using existing `BookingModal` fields), `HERO_MAGAZINE_COVER` (full-bleed image + overlay), `HERO_OFFSET_BRUTALIST`, `HERO_MINIMAL_EDITORIAL`, `HERO_COMPACT_BAR`, `HERO_CYBER_GLOW`, `HERO_CREAM_HERITAGE`. Each with its own DOM structure, spacing scale, and type treatment — not shared `py-24 px-4` containers.
- **Services**: implement `SERVICES_BENTO_TILES`, `SERVICES_SIDE_TABS`, `SERVICES_ACCORDION_LIST`, `SERVICES_HIGHLIGHT_BANNER`, `SERVICES_COMPARISON_TABLE` (the issue's "service comparison matrix"), etc.
- **FAQ / CTA / Reviews / Workflow**: same treatment — one real layout per selected variant string. FAQ gets `FAQ_TABBED_CATEGORIES` + `FAQ_SIDE_SEARCH` (the issue's "inline search"); CTA gets `CTA_SPLIT_APPOINTMENT`, `CTA_STICKY_BOTTOM_BAR`, etc.

I won't necessarily build all 10 of every section on day one; I'll build the ones that actually appear in generated sites first (query the `previews/*.json`), then fill in the rest. Each new variant is additive and independently testable.

Deliverable: two businesses with different seeds now produce **visibly different** pages end-to-end. This is the fix that makes the "every site is the same" complaint go away.

### Phase 2 — Motion + archetype-aware widgets (fixes 1.5, polishes 1.2) — ~1–1.5 days

1. **Use the `framer-motion` that's already installed.** Add a shared `motion` wrapper for scroll-reveal (`whileInView={{ opacity: 1, y: 0 }}`, `viewport={{ once: true }}`), staggered children on card grids, and spring hover on primary buttons. Centralize the variants object so timing is consistent and easy to tune. Respect `prefers-reduced-motion`.
2. **Mount `LiveSlotPicker`** into the hero for `HERO_SIDE_FORM` / booking-focused archetypes, and make all three widgets take `archetype`/palette props so they restyle instead of always looking cyan-glassy.

### Phase 3 — Componentize into the architecture the issue wants (fixes 1.1 cleanly) — ~2 days

Now that variants are live, refactor for maintainability (this is the issue's §1.1, done *after* the value is already shipped):

```
client-template/components/
  sections/
    hero/            HeroSplitShowcase.tsx, HeroBentoGrid.tsx, ...
    services/        ServicesBentoTiles.tsx, ServicesSideTabs.tsx, ...
    faq/  cta/  reviews/  workflow/
  registry.ts        // { HERO_BENTO_GRID: HeroBentoGrid, ... }
```

`DynamicClientSite.tsx` shrinks to a thin orchestrator: read `section_order`, look up `variants[section]` in the registry, render with the theme context from Phase 0. A missing variant falls back gracefully to a safe default. This kills the 600-line monolith and makes adding an archetype a one-file, one-registry-line change.

### Phase 4 — Copy quality (fixes 1.4) — ~0.5 day

In `src/generator/site_generator.py`, upgrade the LLM prompt to demand: local landmarks/neighborhoods, explicit price ranges, a named-practitioner quote, and anxiety-reframing headlines (the issue's example format). Add archetype-conditioned tone (Editorial = warm/narrative, Cyber = precise/technical). Improve the **fallback strings** too, since some sites render them — and add a generation guard so a site is never exported with `archetype: null`.

---

## 3. Sequencing rationale

The issue's own action list starts with "decouple component architecture" (Phase 3 here). I deliberately **reorder** so the user sees differentiated sites in days, not weeks:

```
P0 palette theming  →  P1 wire variants  →  P2 motion+widgets  →  P3 componentize  →  P4 copy
   (unblocks)          (the actual fix)      (premium feel)        (maintainability)   (polish)
```

Each phase is shippable on its own. P0 + P1 together resolve ~80% of the "feels generic" complaint because they turn the already-existing 1.4M-combination engine from *decorative* into *functional*.

## 4. What I need from you to start

- Confirm the priority order above (or tell me if a full P3-first rewrite is preferred despite the slower payoff).
- One decision: **should I keep the single-file renderer through P0–P2 and refactor in P3, or componentize from the first line?** I recommend the former (faster visible results), but it's your call.

> Heads-up on the toolchain: `client-template/AGENTS.md` warns this is a **non-standard Next.js 16.3.1** with breaking changes from stock Next. Before writing components I'll check `node_modules/next/dist/docs/` for the current conventions rather than assuming defaults.
