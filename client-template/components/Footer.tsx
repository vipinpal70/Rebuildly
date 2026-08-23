import React from 'react';
import { MapPin, Phone, Mail, Clock, ShieldCheck, Heart } from 'lucide-react';
import { BusinessData } from '../types/business';

interface FooterProps {
  business: BusinessData;
}

export const Footer: React.FC<FooterProps> = ({ business }) => {
  return (
    <footer className="bg-[#030712] text-slate-400 pt-16 pb-12 border-t border-white/10 px-4 sm:px-8 text-xs">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
        {/* Column 1: Brand */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-indigo-500 flex items-center justify-center text-white font-serif-title font-bold text-lg shadow-md">
              {business.name.charAt(0)}
            </div>
            <span className="font-serif-title font-bold text-lg text-white">
              {business.name}
            </span>
          </div>
          <p className="text-slate-400 text-xs leading-relaxed">
            {business.tagline}
          </p>
          <div className="flex items-center gap-2 text-emerald-400 font-semibold pt-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Verified 5-Star {business.category}</span>
          </div>
        </div>

        {/* Column 2: Quick Links */}
        <div>
          <h4 className="font-serif-title text-sm font-bold text-white mb-4 uppercase tracking-wider text-cyan-400">
            Quick Navigation
          </h4>
          <ul className="space-y-2.5">
            <li>
              <a href="#" className="hover:text-cyan-300 transition-colors">Home Page</a>
            </li>
            <li>
              <a href="#services" className="hover:text-cyan-300 transition-colors">Specialties & Treatments</a>
            </li>
            <li>
              <a href="#why-us" className="hover:text-cyan-300 transition-colors">Why Choose Us</a>
            </li>
            <li>
              <a href="#workflow" className="hover:text-cyan-300 transition-colors">Process & Workflow</a>
            </li>
            <li>
              <a href="#reviews" className="hover:text-cyan-300 transition-colors">Patient Reviews</a>
            </li>
            <li>
              <a href="#faq" className="hover:text-cyan-300 transition-colors">FAQ</a>
            </li>
          </ul>
        </div>

        {/* Column 3: Practice Hours */}
        <div>
          <h4 className="font-serif-title text-sm font-bold text-white mb-4 uppercase tracking-wider text-cyan-400">
            Opening Hours
          </h4>
          <div className="space-y-2.5">
            {business.hours ? (
              <div className="flex items-start gap-2">
                <Clock className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                <span>{business.hours}</span>
              </div>
            ) : (
              <>
                <div>Mon - Fri: 8:00 AM - 6:00 PM</div>
                <div>Sat: 9:00 AM - 2:00 PM</div>
                <div>Sun: Emergency Appointments Only</div>
              </>
            )}
            {business.emergencyPhone && (
              <div className="pt-2 text-emerald-400 font-semibold">
                24/7 Emergency Line: {business.emergencyPhone}
              </div>
            )}
          </div>
        </div>

        {/* Column 4: Contact & Location */}
        <div>
          <h4 className="font-serif-title text-sm font-bold text-white mb-4 uppercase tracking-wider text-cyan-400">
            Clinic Location
          </h4>
          <ul className="space-y-3">
            {business.address && (
              <li className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                <span>{business.address}</span>
              </li>
            )}
            {business.phone && (
              <li className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <a href={`tel:${business.phone}`} className="hover:text-white transition-colors">
                  {business.phone}
                </a>
              </li>
            )}
            {business.email && (
              <li className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <a href={`mailto:${business.email}`} className="hover:text-white transition-colors">
                  {business.email}
                </a>
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* Bottom Hairline & Copyright */}
      <div className="max-w-7xl mx-auto pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
        <p>© {new Date().getFullYear()} {business.name}. All rights reserved.</p>
        <p className="flex items-center gap-1 text-slate-500">
          <span>Modernized with</span>
          <Heart className="w-3 h-3 text-rose-500 fill-rose-500" />
          <span>by Rebuildly</span>
        </p>
      </div>
    </footer>
  );
};
