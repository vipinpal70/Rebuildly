import React from 'react';
import { Calendar, Layers, Activity, Smile } from 'lucide-react';
import { BusinessData } from '../types/business';

interface WorkflowSectionProps {
  business: BusinessData;
}

export const WorkflowSection: React.FC<WorkflowSectionProps> = ({ business }) => {
  const steps = business.workflow || [
    {
      step: '01',
      title: 'Book Consultation Online',
      description: 'Choose your preferred date and service instantly through our 24/7 AI Receptionist system.'
    },
    {
      step: '02',
      title: '3D Scan & Smile Simulation',
      description: 'Visit our clinic for a comfortable, non-invasive 3D intraoral digital scan.'
    },
    {
      step: '03',
      title: 'Personalized Treatment Plan',
      description: 'Review transparent pricing and custom smile options with your senior clinical specialist.'
    },
    {
      step: '04',
      title: 'Radiant Smile Transformation',
      description: 'Receive your precision-engineered restorations with full peace of mind and lifetime care.'
    }
  ];

  return (
    <section id="workflow" className="py-24 px-4 sm:px-8 bg-[#07101f] relative overflow-hidden border-t border-white/10">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 mb-3 bg-cyan-950/50 border border-cyan-400/30 px-4 py-1.5 rounded-full">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>HOW IT WORKS</span>
          </div>
          <h2 className="font-serif-title text-3xl sm:text-5xl font-bold text-white tracking-tight">
            Your Step-by-Step <em className="italic text-cyan-300 font-normal">Journey to Excellence</em>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mt-4">
            From initial booking to final result, we make every step seamless, comfortable, and predictable.
          </p>
        </div>

        {/* 4-Step Process Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {steps.map((st, idx) => (
            <div
              key={idx}
              className="glass-card p-8 rounded-3xl border border-white/10 hover:border-cyan-400/40 transition-all flex flex-col justify-between relative group"
            >
              <div>
                {/* Step Pill */}
                <div className="flex items-center justify-between mb-6">
                  <span className="font-serif-title text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                    {st.step}
                  </span>
                  <div className="w-8 h-8 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-400 flex items-center justify-center text-xs font-bold">
                    ✓
                  </div>
                </div>

                <h3 className="font-serif-title text-lg font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
                  {st.title}
                </h3>
                <p className="text-slate-400 text-xs sm:text-sm leading-relaxed">
                  {st.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
