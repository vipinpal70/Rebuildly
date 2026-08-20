'use client';

import React, { useState } from 'react';
import { Calculator, CheckCircle, ArrowRight, Shield } from 'lucide-react';

interface TreatmentCostCalculatorProps {
  businessName?: string;
  onBookClick?: () => void;
  accentColor?: string;
}

export function TreatmentCostCalculator({
  businessName = "Specialist Practice",
  onBookClick,
  accentColor = "#00b4d8"
}: TreatmentCostCalculatorProps) {
  const [selectedPlan, setSelectedPlan] = useState<'ESSENTIAL' | 'COMPREHENSIVE' | 'PREMIER'>('COMPREHENSIVE');
  const [months, setMonths] = useState<12 | 24 | 36>(12);

  const planPricing = {
    ESSENTIAL: { total: 1200, name: "Essential Treatment", desc: "Single procedure or core targeted restoration." },
    COMPREHENSIVE: { total: 2800, name: "Comprehensive Smile Care", desc: "Multi-tooth alignment, whitening, & restoration." },
    PREMIER: { total: 5500, name: "Premier Full Arch Rehab", desc: "Complete boutique 3D surgical transformation." }
  };

  const currentPlan = planPricing[selectedPlan];
  const monthlyEstimate = (currentPlan.total / months).toFixed(2);

  return (
    <div className="w-full my-12 p-8 sm:p-12 rounded-3xl border border-white/10 bg-slate-900/80 backdrop-blur-xl shadow-2xl">
      <div className="max-w-3xl mx-auto text-center mb-10">
        <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest mb-3" style={{ color: accentColor }}>
          <Calculator className="w-4 h-4" />
          <span>TRANSPARENT PRICING & FINANCING</span>
        </div>
        <h3 className="text-2xl sm:text-4xl font-extrabold mb-3">Instant Monthly Payment Estimator</h3>
        <p className="text-xs sm:text-sm text-slate-400">
          Calculate zero-surprise monthly payment options tailored for patients at {businessName}.
        </p>
      </div>

      {/* Plan Selector Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {(Object.keys(planPricing) as Array<keyof typeof planPricing>).map((key) => {
          const isSelected = selectedPlan === key;
          const plan = planPricing[key];
          return (
            <button
              key={key}
              onClick={() => setSelectedPlan(key)}
              className={`p-6 rounded-2xl border text-left transition-all cursor-pointer ${
                isSelected
                  ? 'border-cyan-400 bg-cyan-500/10 shadow-[0_0_30px_rgba(0,180,216,0.2)]'
                  : 'border-white/10 bg-white/5 hover:border-white/20'
              }`}
            >
              <div className="text-xs font-bold text-slate-400 uppercase mb-1">{key}</div>
              <div className="font-bold text-base mb-2">{plan.name}</div>
              <div className="text-[11px] text-slate-400">{plan.desc}</div>
            </button>
          );
        })}
      </div>

      {/* Term Selector */}
      <div className="p-6 rounded-2xl bg-white/5 border border-white/10 mb-8 flex flex-wrap items-center justify-between gap-6">
        <div>
          <div className="text-xs font-bold uppercase text-slate-300 mb-1">Select Financing Term (0% APR Available)</div>
          <div className="text-xs text-slate-400">Flexible monthly payback duration</div>
        </div>

        <div className="flex items-center gap-3">
          {[12, 24, 36].map((m) => (
            <button
              key={m}
              onClick={() => setMonths(m as any)}
              className={`px-4 py-2 rounded-xl text-xs font-bold border cursor-pointer transition-all ${
                months === m ? 'bg-cyan-500 text-white border-cyan-400' : 'bg-transparent text-slate-300 border-white/10'
              }`}
            >
              {m} Months
            </button>
          ))}
        </div>
      </div>

      {/* Result Display Box */}
      <div className="p-8 rounded-2xl bg-slate-950 border border-white/10 flex flex-wrap items-center justify-between gap-6">
        <div>
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Estimated Monthly Payment</div>
          <div className="text-3xl sm:text-5xl font-extrabold text-cyan-400 font-mono">
            ${monthlyEstimate}<span className="text-sm font-sans font-normal text-slate-400">/mo</span>
          </div>
          <div className="text-[11px] text-emerald-400 flex items-center gap-1 mt-2">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>0% APR financing options subject to qualification</span>
          </div>
        </div>

        <button
          onClick={onBookClick}
          className="px-8 py-4 rounded-xl text-xs font-bold text-white uppercase tracking-wider bg-cyan-600 hover:bg-cyan-500 transition-all shadow-xl flex items-center gap-2 cursor-pointer"
        >
          <span>Apply for Financing</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
