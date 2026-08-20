import React from 'react';
import { BusinessData } from '../types/business';

interface TrustStripProps {
  business: BusinessData;
}

export const TrustStrip: React.FC<TrustStripProps> = ({ business }) => {
  const stats = business.stats || [
    { number: '99.8%', label: 'PATIENT SATISFACTION RATE' },
    { number: '15,000+', label: 'SMILES TRANSFORMED' },
    { number: '24/7', label: 'AI ASSISTED APPOINTMENTS' },
    { number: '0 Min', label: 'AVERAGE WAITING ROOM TIME' }
  ];

  return (
    <section className="bg-[#050b17] border-y border-white/10 py-12 px-4 sm:px-8 relative overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((st, idx) => (
            <div
              key={idx}
              className="glass-card p-6 rounded-2xl text-center flex flex-col items-center justify-center border border-white/5 hover:border-cyan-500/30 transition-all group"
            >
              <span className="font-serif-title text-3xl sm:text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-cyan-300 group-hover:scale-105 transition-transform duration-300">
                {st.number}
              </span>
              <span className="text-[11px] font-bold tracking-widest text-cyan-400/90 uppercase mt-3 text-center">
                {st.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
