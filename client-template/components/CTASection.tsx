import React from 'react';
import { Calendar, Phone, ArrowRight, Sparkles, CheckCircle } from 'lucide-react';
import { BusinessData } from '../types/business';

interface CTASectionProps {
  business: BusinessData;
  onOpenBooking: () => void;
}

export const CTASection: React.FC<CTASectionProps> = ({ business, onOpenBooking }) => {
  return (
    <section className="py-24 px-4 sm:px-8 bg-[#040914] relative overflow-hidden border-t border-white/10">
      {/* Background Radial Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-r from-blue-600/30 via-cyan-500/20 to-indigo-600/30 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="max-w-5xl mx-auto glass-card p-10 sm:p-16 rounded-[40px] border border-cyan-500/30 text-center relative z-10 shadow-2xl overflow-hidden">
        <div className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-300 bg-cyan-950/80 border border-cyan-400/40 px-4 py-1.5 rounded-full mb-6">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>TRANSFORM YOUR SMILE TODAY</span>
        </div>

        <h2 className="font-serif-title text-3xl sm:text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-3xl mx-auto mb-6">
          Ready to Experience <em className="italic text-cyan-300 font-normal">Next-Gen Care?</em>
        </h2>

        <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-10 leading-relaxed">
          Book your consultation in under 60 seconds with our instant 24/7 AI Receptionist. No waiting queues, instant confirmation.
        </p>

        {/* Dual CTAs */}
        <div className="flex flex-wrap items-center justify-center gap-4 max-w-md mx-auto">
          <button
            onClick={onOpenBooking}
            className="w-full sm:w-auto flex-1 gradient-btn-primary px-8 py-4 rounded-2xl text-sm font-bold text-white tracking-wide uppercase inline-flex items-center justify-center gap-3 group cursor-pointer shadow-xl"
          >
            <Calendar className="w-4 h-4" />
            <span>Book Appointment</span>
            <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
          </button>

          {business.phone && (
            <a
              href={`tel:${business.phone}`}
              className="w-full sm:w-auto flex-1 bg-white/10 hover:bg-white/18 border border-white/20 px-7 py-4 rounded-2xl text-sm font-semibold text-white tracking-wide inline-flex items-center justify-center gap-2 backdrop-blur-md transition-all hover:-translate-y-0.5"
            >
              <Phone className="w-4 h-4 text-cyan-400" />
              <span>Call Us Direct</span>
            </a>
          )}
        </div>

        {/* Confidence checkmarks */}
        <div className="flex flex-wrap items-center justify-center gap-6 mt-10 pt-8 border-t border-white/10 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>Instant Confirmation</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>0% Interest Payment Options</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>5-Star Rated Service</span>
          </div>
        </div>
      </div>
    </section>
  );
};
