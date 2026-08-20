import React from 'react';
import { Star, Calendar, ArrowRight, ShieldCheck, CheckCircle2, Sparkles } from 'lucide-react';
import { BusinessData } from '../types/business';

interface HeroSectionProps {
  business: BusinessData;
  onOpenBooking: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ business, onOpenBooking }) => {
  const badgeText = business.badgeText || `🔥 #1 RATED ${business.category.toUpperCase()} IN ${business.city.toUpperCase()}`;

  return (
    <section className="relative min-h-[85vh] flex flex-col justify-center items-center text-center px-4 sm:px-8 py-20 overflow-hidden hero-dot-pattern">
      {/* Background Radial Glow Spotlights */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[450px] bg-gradient-to-tr from-blue-600/20 via-cyan-500/15 to-indigo-600/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-cyan-600/10 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="relative z-10 max-w-5xl mx-auto flex flex-col items-center">
        {/* Animated Status Pill */}
        <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-blue-950/70 border border-cyan-400/30 text-cyan-300 text-xs font-bold tracking-wider uppercase backdrop-blur-xl shadow-lg mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse-dot"></span>
          <span>{badgeText}</span>
        </div>

        {/* Playfair Display Headline with Glowing Italicized Text */}
        <h1 className="font-serif-title text-4xl sm:text-6xl md:text-7xl font-extrabold text-white leading-[1.08] tracking-tight max-w-4xl mb-6">
          Experience <em className="italic text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300 font-normal">World-Class</em> {business.category} in {business.city}
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg md:text-xl text-slate-300 max-w-2xl leading-relaxed mb-8">
          {business.heroSubtitle || business.tagline}
        </p>

        {/* Google Rating Star Badge */}
        <div className="inline-flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-5 py-2 mb-10 backdrop-blur-md">
          <div className="flex text-amber-400 gap-0.5">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="w-4 h-4 fill-amber-400" />
            ))}
          </div>
          <span className="text-xs font-semibold text-white">
            {business.google_rating} / 5.0 Rating ({business.review_count} Verified Google Reviews)
          </span>
        </div>

        {/* Dual High-Converting CTAs */}
        <div className="flex flex-wrap items-center justify-center gap-4 w-full max-w-md">
          <button
            onClick={onOpenBooking}
            className="w-full sm:w-auto flex-1 gradient-btn-primary px-8 py-4 rounded-2xl text-sm font-bold text-white tracking-wide uppercase inline-flex items-center justify-center gap-3 group shadow-xl cursor-pointer"
          >
            <Calendar className="w-4 h-4" />
            <span>Book Consultation</span>
            <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
          </button>

          <a
            href="#services"
            className="w-full sm:w-auto flex-1 bg-white/10 hover:bg-white/18 border border-white/20 px-7 py-4 rounded-2xl text-sm font-semibold text-white tracking-wide inline-flex items-center justify-center gap-2 backdrop-blur-md transition-all hover:-translate-y-0.5"
          >
            <span>Explore Services</span>
          </a>
        </div>

        {/* Floating Glass Feature Badges Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-16 w-full max-w-3xl">
          <div className="glass-card p-4 rounded-2xl text-left flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-400/30 flex items-center justify-center text-cyan-400 flex-shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">100% Guaranteed</div>
              <div className="text-[11px] text-slate-400">Painless Protocols</div>
            </div>
          </div>

          <div className="glass-card p-4 rounded-2xl text-left flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 border border-blue-400/30 flex items-center justify-center text-blue-400 flex-shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">3D Digital Precision</div>
              <div className="text-[11px] text-slate-400">State-of-the-art Tech</div>
            </div>
          </div>

          <div className="glass-card p-4 rounded-2xl text-left flex items-center gap-3 col-span-2 sm:col-span-1">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center text-emerald-400 flex-shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-white">Same-Day Slots</div>
              <div className="text-[11px] text-slate-400">24/7 AI Booking</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
