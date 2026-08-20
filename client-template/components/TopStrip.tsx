import React from 'react';
import { Phone, Clock, MapPin, Calendar } from 'lucide-react';
import { BusinessData } from '../types/business';

interface TopStripProps {
  business: BusinessData;
  onOpenBooking: () => void;
}

export const TopStrip: React.FC<TopStripProps> = ({ business, onOpenBooking }) => {
  return (
    <div className="bg-[#040914] border-b border-white/5 text-xs text-slate-400 py-2 px-4 sm:px-8 transition-all">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Left Info */}
        <div className="flex items-center gap-6 flex-wrap">
          <div className="flex items-center gap-1.5 hover:text-white transition-colors">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            <span>{business.city}, {business.country}</span>
          </div>

          {business.hours && (
            <div className="hidden md:flex items-center gap-1.5 hover:text-white transition-colors">
              <Clock className="w-3.5 h-3.5 text-blue-400" />
              <span>{business.hours}</span>
            </div>
          )}

          {business.emergencyPhone && (
            <div className="hidden lg:flex items-center gap-1.5 text-emerald-400 font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>24/7 Emergency Line: {business.emergencyPhone}</span>
            </div>
          )}
        </div>

        {/* Right Info & Actions */}
        <div className="flex items-center gap-4 ml-auto">
          {business.phone && (
            <a
              href={`tel:${business.phone}`}
              className="flex items-center gap-1.5 text-slate-300 hover:text-cyan-400 transition-colors font-medium"
            >
              <Phone className="w-3.5 h-3.5 text-cyan-400" />
              <span>{business.phone}</span>
            </a>
          )}

          <button
            onClick={onOpenBooking}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-300 hover:text-white bg-cyan-950/60 hover:bg-cyan-900/60 px-3 py-1 rounded-full border border-cyan-500/30 transition-all cursor-pointer"
          >
            <Calendar className="w-3 h-3" />
            <span>Book Online</span>
          </button>
        </div>
      </div>
    </div>
  );
};
