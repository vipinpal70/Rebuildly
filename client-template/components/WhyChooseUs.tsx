import React from 'react';
import { Sparkles, Clock, ShieldCheck, Zap, Award, Heart, Shield, CheckCircle2 } from 'lucide-react';
import { BusinessData } from '../types/business';

interface WhyChooseUsProps {
  business: BusinessData;
}

export const WhyChooseUs: React.FC<WhyChooseUsProps> = ({ business }) => {
  const iconMap: Record<string, React.ReactNode> = {
    sparkles: <Sparkles className="w-6 h-6 text-cyan-400" />,
    clock: <Clock className="w-6 h-6 text-blue-400" />,
    shield: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
    zap: <Zap className="w-6 h-6 text-amber-400" />,
    award: <Award className="w-6 h-6 text-purple-400" />,
    heart: <Heart className="w-6 h-6 text-rose-400" />
  };

  const usps = business.usps || [
    {
      icon: 'sparkles',
      title: 'Digital 3D Smile Design',
      description: 'Preview your exact smile transformation on a 3D digital model before treatment even begins.'
    },
    {
      icon: 'clock',
      title: '24/7 Instant Online Booking',
      description: 'No waiting on hold. Reserve your appointment in under 60 seconds with real-time slot sync.'
    },
    {
      icon: 'shield',
      title: 'Painless & Gentle Guarantee',
      description: 'State-of-the-art needle-free sedation and gentle care protocols for anxious patients.'
    },
    {
      icon: 'zap',
      title: 'Same-Day Emergency Relief',
      description: 'Dedicated priority slots reserved every day to relieve acute pain and dental emergencies immediately.'
    },
    {
      icon: 'award',
      title: '10-Year Comprehensive Warranty',
      description: 'We back all dental implants, veneers, and full-mouth restorations with a written guarantee.'
    },
    {
      icon: 'heart',
      title: '0% Interest Financing',
      description: 'Flexible payment plans up to 24 months to make world-class cosmetic dentistry affordable.'
    }
  ];

  return (
    <section id="why-us" className="py-24 px-4 sm:px-8 bg-[#050b17] relative overflow-hidden border-t border-white/10">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 mb-3 bg-cyan-950/50 border border-cyan-400/30 px-4 py-1.5 rounded-full">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>THE {business.name.toUpperCase()} DIFFERENCE</span>
          </div>
          <h2 className="font-serif-title text-3xl sm:text-5xl font-bold text-white tracking-tight">
            Why Patients Choose <em className="italic text-cyan-300 font-normal">{business.name}</em>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-4">
            We pair advanced clinical technology with gentle human care to give you the highest quality experience in {business.city}.
          </p>
        </div>

        {/* 6-Cell Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {usps.map((u, idx) => (
            <div
              key={idx}
              className="glass-card p-8 rounded-3xl border border-white/10 hover:border-cyan-400/40 transition-all group relative overflow-hidden"
            >
              <div className="w-14 h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:border-cyan-400/50 transition-all duration-300">
                {iconMap[u.icon] || <Sparkles className="w-6 h-6 text-cyan-400" />}
              </div>

              <h3 className="font-serif-title text-xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
                {u.title}
              </h3>
              <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                {u.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
