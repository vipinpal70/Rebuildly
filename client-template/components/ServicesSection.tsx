import React, { useState } from 'react';
import { Check, ArrowUpRight, Calendar, Sparkles } from 'lucide-react';
import { BusinessData, DetailedService } from '../types/business';

interface ServicesSectionProps {
  business: BusinessData;
  onOpenBooking: () => void;
}

export const ServicesSection: React.FC<ServicesSectionProps> = ({ business, onOpenBooking }) => {
  const detailedServices = business.detailedServices || [];
  const categories = ['ALL', ...Array.from(new Set(detailedServices.map((s) => s.category)))];
  const [activeCategory, setActiveCategory] = useState('ALL');

  const filteredServices = activeCategory === 'ALL'
    ? detailedServices
    : detailedServices.filter((s) => s.category === activeCategory);

  return (
    <section id="services" className="py-24 px-4 sm:px-8 relative bg-[#07101f]">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 mb-3">
              <Sparkles className="w-4 h-4" />
              <span>CLINICAL EXCELLENCE & SERVICES</span>
            </div>
            <h2 className="font-serif-title text-3xl sm:text-5xl font-bold text-white tracking-tight">
              Specialized <em className="italic text-cyan-300 font-normal">Care & Treatments</em>
            </h2>
          </div>

          <p className="text-slate-400 text-sm max-w-md">
            Engineered with precision digital technology to deliver long-lasting, pain-free results tailored to your unique smile.
          </p>
        </div>

        {/* Category Filter Tabs */}
        {categories.length > 2 && (
          <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-10 no-scrollbar">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-5 py-2.5 rounded-full text-xs font-bold tracking-wider uppercase whitespace-nowrap transition-all cursor-pointer ${
                  activeCategory === cat
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                    : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 border border-white/10'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {/* Services Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredServices.map((srv, idx) => (
            <div
              key={idx}
              className="glass-card rounded-3xl p-8 flex flex-col justify-between group border border-white/10 hover:border-cyan-500/40 relative overflow-hidden transition-all duration-300"
            >
              {/* Radial background glow on hover */}
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>

              <div>
                {/* Arrow Top Right */}
                <div className="flex items-center justify-between mb-6">
                  <span className="text-[10px] font-extrabold tracking-widest uppercase text-cyan-400 bg-cyan-950/80 border border-cyan-500/30 px-3 py-1 rounded-full">
                    {srv.category}
                  </span>
                  <div className="w-10 h-10 rounded-full border border-white/15 group-hover:border-cyan-400 group-hover:bg-cyan-500 text-slate-300 group-hover:text-white flex items-center justify-center transition-all duration-300 group-hover:rotate-45">
                    <ArrowUpRight className="w-5 h-5" />
                  </div>
                </div>

                <h3 className="font-serif-title text-xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
                  {srv.title}
                </h3>
                <p className="text-slate-400 text-xs sm:text-sm leading-relaxed mb-6">
                  {srv.description}
                </p>

                {/* Features Checklist */}
                {srv.features && srv.features.length > 0 && (
                  <ul className="space-y-2 mb-8 pt-4 border-t border-white/10">
                    {srv.features.map((feat, fIdx) => (
                      <li key={fIdx} className="flex items-center gap-2.5 text-xs text-slate-300">
                        <div className="w-4 h-4 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0">
                          <Check className="w-3 h-3 stroke-[3]" />
                        </div>
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Bottom CTA Button */}
              <button
                onClick={onOpenBooking}
                className="w-full py-3 rounded-xl bg-white/5 hover:bg-cyan-600 text-xs font-bold text-slate-200 hover:text-white border border-white/10 hover:border-cyan-500 transition-all flex items-center justify-center gap-2 cursor-pointer group-hover:shadow-lg"
              >
                <Calendar className="w-3.5 h-3.5" />
                <span>Book This Treatment</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
