import React, { useState } from 'react';
import { Plus, Minus, HelpCircle } from 'lucide-react';
import { BusinessData } from '../types/business';

interface FAQSectionProps {
  business: BusinessData;
}

export const FAQSection: React.FC<FAQSectionProps> = ({ business }) => {
  const faqs = business.faqs || [
    {
      question: 'How do I book an emergency appointment for dental pain?',
      answer: 'You can book an immediate emergency slot 24/7 using our live online receptionist or by calling our priority line. We reserve same-day emergency slots daily.'
    },
    {
      question: 'Are cosmetic treatments like Invisalign and Veneers painful?',
      answer: 'Not at all. We utilize non-invasive digital scanning and gentle sedation options to ensure a completely comfortable, pain-free experience.'
    },
    {
      question: 'Do you offer flexible payment plans for dental implants?',
      answer: 'Yes! We offer 0% APR financing spread across 6, 12, or 24 months so you can receive immediate treatment with manageable monthly payments.'
    },
    {
      question: 'What makes digital 3D dentistry superior to traditional molds?',
      answer: 'Digital 3D intraoral scans take under 2 minutes, eliminate uncomfortable impression putty, and deliver 10x greater precision for long-lasting results.'
    }
  ];

  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggleIndex = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  return (
    <section id="faq" className="py-24 px-4 sm:px-8 bg-[#07101f] relative overflow-hidden border-t border-white/10">
      <div className="max-w-4xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 mb-3 bg-cyan-950/50 border border-cyan-400/30 px-4 py-1.5 rounded-full">
            <HelpCircle className="w-4 h-4 text-cyan-400" />
            <span>GOT QUESTIONS?</span>
          </div>
          <h2 className="font-serif-title text-3xl sm:text-5xl font-bold text-white tracking-tight">
            Frequently Asked <em className="italic text-cyan-300 font-normal">Questions</em>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-4">
            Everything you need to know about visiting {business.name} in {business.city}.
          </p>
        </div>

        {/* Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = openIdx === idx;
            return (
              <div
                key={idx}
                className="glass-card rounded-2xl border border-white/10 overflow-hidden transition-all duration-200"
              >
                <button
                  onClick={() => toggleIndex(idx)}
                  className="w-full p-6 text-left flex items-center justify-between gap-4 cursor-pointer hover:bg-white/5 transition-colors"
                >
                  <span className="font-serif-title text-base sm:text-lg font-semibold text-white">
                    {faq.question}
                  </span>
                  <div className={`w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-cyan-400 flex-shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180 bg-cyan-500/20 border-cyan-400/40' : ''}`}>
                    {isOpen ? <Minus className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-6 pb-6 text-xs sm:text-sm text-slate-300 leading-relaxed border-t border-white/5 pt-4 animate-in fade-in duration-200">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
