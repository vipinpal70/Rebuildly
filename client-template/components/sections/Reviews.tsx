'use client';

import React from 'react';
import { Quote, BadgeCheck } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, Stagger, StaggerItem, SectionHeading, Section, Card, Stars, Avatar } from '../site/ui';
import { siteCopy } from '../site/copy';

function useReviews() {
  const { config: c, theme: t } = useSite();
  return { c, t, reviews: c.reviews || [] };
}

const HEAD = (c: any) => ({ eyebrow: 'Social Proof', title: `Verified ${siteCopy(c).audienceTitle} Reviews in`, accent: c.city });

function ReviewBody({ r }: { r: any }) {
  const { theme: t } = useSite();
  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <Stars n={r.rating || 5} />
        {r.resultBadge && (
          <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full" style={{ backgroundColor: t.badgeBg, color: t.badgeText }}>
            <BadgeCheck className="w-3 h-3" />{r.resultBadge}
          </span>
        )}
      </div>
      <p className="text-sm italic leading-relaxed mb-6" style={{ color: t.subtext }}>&ldquo;{r.text}&rdquo;</p>
      <div className="flex items-center gap-3 pt-4" style={{ borderTop: `1px solid ${t.hairline}` }}>
        <Avatar letter={r.avatarLetter || r.author?.charAt(0)} />
        <div><div className="font-bold text-sm" style={{ color: t.text }}>{r.author}</div><div className="text-[11px]" style={{ color: t.subtext }}>{r.relativeTime}</div></div>
      </div>
    </>
  );
}

function ThreeCol() {
  const { c, reviews } = useReviews();
  return (
    <Section id="reviews" tint>
      <Reveal><SectionHeading {...HEAD(c)} /></Reveal>
      <Stagger className="grid md:grid-cols-3 gap-6">
        {reviews.map((r: any, i: number) => (<StaggerItem key={i}><Card className="p-8 h-full"><ReviewBody r={r} /></Card></StaggerItem>))}
      </Stagger>
    </Section>
  );
}

function Spotlight() {
  const { c, t, reviews } = useReviews();
  const [feat, ...rest] = reviews;
  if (!feat) return <ThreeCol />;
  return (
    <Section id="reviews" tint>
      <div className="grid lg:grid-cols-12 gap-8 items-center">
        <Reveal className="lg:col-span-7">
          <Card hover={false} className="p-10 relative">
            <Quote className="w-12 h-12 mb-4" style={{ color: withAlpha(t.accent, 0.4) }} />
            <p className="text-xl sm:text-2xl leading-relaxed mb-6" style={{ fontFamily: t.serifFamily, color: t.text }}>&ldquo;{feat.text}&rdquo;</p>
            <div className="flex items-center gap-3"><Avatar letter={feat.avatarLetter || feat.author?.charAt(0)} /><div><div className="font-bold" style={{ color: t.text }}>{feat.author}</div><Stars n={feat.rating || 5} /></div></div>
          </Card>
        </Reveal>
        <div className="lg:col-span-5 space-y-4">
          <Reveal><SectionHeading {...HEAD(c)} center={false} /></Reveal>
          {rest.slice(0, 2).map((r: any, i: number) => (
            <Reveal key={i} delay={0.1 + i * 0.08}><Card className="p-6"><ReviewBody r={r} /></Card></Reveal>
          ))}
        </div>
      </div>
    </Section>
  );
}

function CarouselSwipe() {
  const { c, reviews } = useReviews();
  return (
    <Section id="reviews" tint>
      <Reveal><SectionHeading {...HEAD(c)} center={false} /></Reveal>
      <div className="flex gap-6 overflow-x-auto pb-6 snap-x" style={{ scrollbarWidth: 'thin' }}>
        {reviews.map((r: any, i: number) => (
          <div key={i} className="snap-start shrink-0 w-[340px]"><Card className="p-8 h-full"><ReviewBody r={r} /></Card></div>
        ))}
      </div>
    </Section>
  );
}

function Masonry() {
  const { c, reviews } = useReviews();
  return (
    <Section id="reviews" tint>
      <Reveal><SectionHeading {...HEAD(c)} /></Reveal>
      <div className="columns-1 md:columns-2 lg:columns-3 gap-6 [column-fill:_balance]">
        {reviews.map((r: any, i: number) => (
          <Reveal key={i} delay={i * 0.05}><div className="mb-6 break-inside-avoid"><Card className="p-8"><ReviewBody r={r} /></Card></div></Reveal>
        ))}
      </div>
    </Section>
  );
}

function TestimonialHero() {
  const { c, t, reviews } = useReviews();
  const feat = reviews[0];
  if (!feat) return <ThreeCol />;
  return (
    <Section id="reviews" tint>
      <Reveal>
        <div className="max-w-3xl mx-auto text-center">
          <Stars className="w-6 h-6" /><div className="flex justify-center mb-6" />
          <p className="text-2xl sm:text-4xl leading-snug mb-8" style={{ fontFamily: t.serifFamily, color: t.text }}>&ldquo;{feat.text}&rdquo;</p>
          <div className="flex items-center justify-center gap-3">
            <Avatar letter={feat.avatarLetter || feat.author?.charAt(0)} />
            <div className="text-left"><div className="font-bold" style={{ color: t.text }}>{feat.author}</div><div className="text-xs" style={{ color: t.subtext }}>Verified {siteCopy(c).audience} · {c.city}</div></div>
          </div>
        </div>
      </Reveal>
    </Section>
  );
}

const MAP: Record<string, React.FC> = {
  REVIEWS_3COL_CARDS: ThreeCol,
  REVIEWS_FEATURED_SPOTLIGHT: Spotlight,
  REVIEWS_CAROUSEL_SWIPE: CarouselSwipe,
  REVIEWS_MASONRY_GRID: Masonry,
  REVIEWS_TESTIMONIAL_HERO: TestimonialHero,
};

export default function Reviews() {
  const { config } = useSite();
  const v = config.layout_tree?.variants?.reviews || 'REVIEWS_3COL_CARDS';
  const Cmp = MAP[v] || ThreeCol;
  return <Cmp />;
}
