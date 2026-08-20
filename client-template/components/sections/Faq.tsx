'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Minus, HelpCircle, Search, MessageSquare } from 'lucide-react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, SectionHeading, Section, Card, PrimaryButton } from '../site/ui';
import { siteCopy } from '../site/copy';

function useFaqs() {
  const { config: c, theme: t, openBooking } = useSite();
  return { c, t, openBooking, faqs: c.faqs || [] };
}

function AccordionItem({ q, a, open, onClick }: { q: string; a: string; open: boolean; onClick: () => void }) {
  const { theme: t } = useSite();
  return (
    <Card hover={false} className="overflow-hidden">
      <button onClick={onClick} className="w-full p-6 text-left flex items-center justify-between gap-4 cursor-pointer">
        <span className="font-semibold text-base sm:text-lg" style={{ color: t.text }}>{q}</span>
        {open ? <Minus className="w-5 h-5 shrink-0" style={{ color: t.accent }} /> : <Plus className="w-5 h-5 shrink-0" style={{ color: t.accent }} />}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
            <div className="px-6 pb-6 pt-4 text-sm leading-relaxed" style={{ borderTop: `1px solid ${t.hairline}`, color: t.subtext }}>{a}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

const HEAD = { eyebrow: 'Answers', icon: <HelpCircle className="w-4 h-4" />, title: 'Frequently Asked', accent: 'Questions' };

function Accordion() {
  const { faqs } = useFaqs();
  const [open, setOpen] = useState(0);
  return (
    <Section id="faq">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="max-w-4xl mx-auto space-y-4">
        {faqs.map((f: any, i: number) => (
          <Reveal key={i} delay={i * 0.04}><AccordionItem q={f.question} a={f.answer} open={open === i} onClick={() => setOpen(open === i ? -1 : i)} /></Reveal>
        ))}
      </div>
    </Section>
  );
}

function TwoColGrid() {
  const { t, faqs } = useFaqs();
  return (
    <Section id="faq">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="grid md:grid-cols-2 gap-5 max-w-5xl mx-auto">
        {faqs.map((f: any, i: number) => (
          <Reveal key={i} delay={i * 0.05}>
            <Card className="p-7 h-full">
              <div className="flex items-start gap-3 mb-3">
                <HelpCircle className="w-5 h-5 shrink-0 mt-0.5" style={{ color: t.accent }} />
                <h3 className="font-bold" style={{ color: t.text }}>{f.question}</h3>
              </div>
              <p className="text-sm leading-relaxed pl-8" style={{ color: t.subtext }}>{f.answer}</p>
            </Card>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

function SideBySide() {
  const { c, t, openBooking, faqs } = useFaqs();
  const [open, setOpen] = useState(0);
  return (
    <Section id="faq">
      <div className="grid lg:grid-cols-12 gap-12">
        <Reveal className="lg:col-span-5">
          <SectionHeading {...HEAD} center={false} subtitle={`Everything ${siteCopy(c).audience} in ${c.city} commonly ask.`} />
          <PrimaryButton onClick={openBooking}>Ask Us Directly</PrimaryButton>
        </Reveal>
        <div className="lg:col-span-7 space-y-4">
          {faqs.map((f: any, i: number) => (
            <Reveal key={i} delay={i * 0.04}><AccordionItem q={f.question} a={f.answer} open={open === i} onClick={() => setOpen(open === i ? -1 : i)} /></Reveal>
          ))}
        </div>
      </div>
    </Section>
  );
}

function SideSearch() {
  const { t, faqs } = useFaqs();
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(0);
  const list = faqs.filter((f: any) => (f.question + f.answer).toLowerCase().includes(q.toLowerCase()));
  return (
    <Section id="faq">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="max-w-3xl mx-auto">
        <Reveal>
          <div className="flex items-center gap-3 px-5 py-4 mb-8 rounded-2xl border" style={{ borderColor: t.border, backgroundColor: t.surface }}>
            <Search className="w-5 h-5" style={{ color: t.accent }} />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search questions…"
              className="flex-1 bg-transparent outline-none text-sm" style={{ color: t.text }} />
          </div>
        </Reveal>
        <div className="space-y-4">
          {list.map((f: any, i: number) => (
            <AccordionItem key={i} q={f.question} a={f.answer} open={open === i} onClick={() => setOpen(open === i ? -1 : i)} />
          ))}
          {!list.length && <p className="text-center text-sm" style={{ color: t.subtext }}>No matches — try another term.</p>}
        </div>
      </div>
    </Section>
  );
}

function MinimalList() {
  const { t, faqs } = useFaqs();
  const [open, setOpen] = useState(0);
  return (
    <Section id="faq">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="max-w-3xl mx-auto">
        {faqs.map((f: any, i: number) => (
          <Reveal key={i} delay={i * 0.04}>
            <div style={{ borderBottom: `1px solid ${t.hairline}` }}>
              <button onClick={() => setOpen(open === i ? -1 : i)} className="w-full py-6 flex items-center justify-between gap-4 text-left cursor-pointer">
                <span className="text-lg font-medium" style={{ fontFamily: t.serifFamily, color: t.text }}>{f.question}</span>
                {open === i ? <Minus className="w-4 h-4" style={{ color: t.accent }} /> : <Plus className="w-4 h-4" style={{ color: t.accent }} />}
              </button>
              <AnimatePresence>
                {open === i && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
                    <p className="pb-6 text-sm leading-relaxed" style={{ color: t.subtext }}>{f.answer}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

function FloatingBubbles() {
  const { t, faqs } = useFaqs();
  return (
    <Section id="faq">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="max-w-3xl mx-auto space-y-6">
        {faqs.map((f: any, i: number) => (
          <Reveal key={i} delay={i * 0.05} className={i % 2 ? 'flex justify-end' : ''}>
            <div className="max-w-[85%]">
              <div className="inline-flex items-center gap-2 text-sm font-bold mb-2" style={{ color: t.text }}>
                <MessageSquare className="w-4 h-4" style={{ color: t.accent }} />{f.question}
              </div>
              <div className="p-5 text-sm leading-relaxed" style={{
                color: t.subtext, backgroundColor: t.surface, border: `1px solid ${t.border}`,
                borderRadius: i % 2 ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
              }}>{f.answer}</div>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

const MAP: Record<string, React.FC> = {
  FAQ_ACCORDION_CLEAN: Accordion,
  FAQ_DARK_GLASS: Accordion,
  FAQ_BORDERED_BOXES: TwoColGrid,
  FAQ_2COL_GRID: TwoColGrid,
  FAQ_HELP_CENTER_CARDS: TwoColGrid,
  FAQ_SIDE_BY_SIDE: SideBySide,
  FAQ_SIDE_SEARCH: SideSearch,
  FAQ_TABBED_CATEGORIES: SideSearch,
  FAQ_MINIMAL_LIST: MinimalList,
  FAQ_FLOATING_BUBBLES: FloatingBubbles,
};

export default function Faq() {
  const { config } = useSite();
  const v = config.layout_tree?.variants?.faq || 'FAQ_ACCORDION_CLEAN';
  const Cmp = MAP[v] || Accordion;
  return <Cmp />;
}
