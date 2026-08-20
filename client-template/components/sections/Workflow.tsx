'use client';

import React from 'react';
import { useSite } from '../site/SiteProvider';
import { withAlpha } from '../site/theme';
import { Reveal, Stagger, StaggerItem, SectionHeading, Section, Card } from '../site/ui';

function useWorkflow() {
  const { config: c, theme: t } = useSite();
  return { c, t, steps: c.workflow || [] };
}

const HEAD = { eyebrow: 'How it works', title: 'Your Care', accent: 'Journey' };

function FourStep() {
  const { t, steps } = useWorkflow();
  return (
    <Section id="workflow">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <Stagger className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {steps.map((s: any, i: number) => (
          <StaggerItem key={i}>
            <Card className="p-8 h-full">
              <span className="text-5xl font-extrabold block mb-4" style={{ fontFamily: t.serifFamily, color: withAlpha(t.accent, 0.9) }}>{s.step}</span>
              <h3 className="text-lg font-bold mb-2" style={{ color: t.text }}>{s.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: t.subtext }}>{s.description}</p>
            </Card>
          </StaggerItem>
        ))}
      </Stagger>
    </Section>
  );
}

function Timeline() {
  const { t, steps } = useWorkflow();
  return (
    <Section id="workflow">
      <Reveal><SectionHeading {...HEAD} center={false} /></Reveal>
      <div className="max-w-3xl relative">
        <div className="absolute left-6 top-2 bottom-2 w-px" style={{ backgroundColor: t.border }} />
        <div className="space-y-8">
          {steps.map((s: any, i: number) => (
            <Reveal key={i} delay={i * 0.08} className="relative pl-20">
              <span className="absolute left-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-white" style={{ background: t.primaryGradient }}>{s.step}</span>
              <h3 className="text-lg font-bold mb-1" style={{ color: t.text }}>{s.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: t.subtext }}>{s.description}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </Section>
  );
}

function Horizontal() {
  const { t, steps } = useWorkflow();
  return (
    <Section id="workflow">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="grid md:grid-cols-4 gap-4 relative">
        {steps.map((s: any, i: number) => (
          <Reveal key={i} delay={i * 0.08}>
            <div className="text-center px-4">
              <div className="w-14 h-14 rounded-2xl mx-auto mb-5 flex items-center justify-center font-extrabold text-white text-lg" style={{ background: t.primaryGradient }}>{s.step}</div>
              <h3 className="font-bold mb-2" style={{ color: t.text }}>{s.title}</h3>
              <p className="text-xs leading-relaxed" style={{ color: t.subtext }}>{s.description}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

function BentoProcess() {
  const { t, steps } = useWorkflow();
  return (
    <Section id="workflow">
      <Reveal><SectionHeading {...HEAD} /></Reveal>
      <div className="grid md:grid-cols-2 gap-5">
        {steps.map((s: any, i: number) => (
          <Reveal key={i} delay={i * 0.06}>
            <Card className={`p-8 h-full flex items-start gap-5 ${i === 0 ? 'md:col-span-2' : ''}`}>
              <span className="text-4xl font-extrabold shrink-0" style={{ fontFamily: t.serifFamily, color: t.accent }}>{s.step}</span>
              <div><h3 className="text-lg font-bold mb-1" style={{ color: t.text }}>{s.title}</h3><p className="text-sm leading-relaxed" style={{ color: t.subtext }}>{s.description}</p></div>
            </Card>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}

const MAP: Record<string, React.FC> = {
  WORKFLOW_4STEP_CARDS: FourStep,
  WORKFLOW_TIMELINE_VERTICAL: Timeline,
  WORKFLOW_HORIZONTAL_STEPS: Horizontal,
  WORKFLOW_BENTO_PROCESS: BentoProcess,
};

export default function Workflow() {
  const { config } = useSite();
  const v = config.layout_tree?.variants?.workflow || 'WORKFLOW_4STEP_CARDS';
  const Cmp = MAP[v] || FourStep;
  return <Cmp />;
}
