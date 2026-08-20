import React, { useState } from 'react';
import { Phone, Calendar, ChevronDown, Menu, X, Sparkles, Shield, Award, ArrowRight } from 'lucide-react';
import { BusinessData } from '../types/business';

interface HeaderProps {
  business: BusinessData;
  onOpenBooking: () => void;
}

export const Header: React.FC<HeaderProps> = ({ business, onOpenBooking }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isServicesDropOpen, setIsServicesDropOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 glass-nav border-b border-white/10 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo & Title */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-cyan-500 to-indigo-500 flex items-center justify-center text-white font-serif-title font-bold text-xl shadow-lg shadow-blue-500/25 group-hover:scale-105 transition-transform">
            {business.name.charAt(0)}
          </div>
          <div className="flex flex-col">
            <span className="font-serif-title font-bold text-lg tracking-tight text-white group-hover:text-cyan-300 transition-colors">
              {business.name}
            </span>
            <span className="text-[11px] text-slate-400 font-medium tracking-wide uppercase">
              {business.category} • {business.city}
            </span>
          </div>
        </a>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          <a href="#" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all">
            Home
          </a>

          {/* Services Dropdown */}
          <div
            className="relative"
            onMouseEnter={() => setIsServicesDropOpen(true)}
            onMouseLeave={() => setIsServicesDropOpen(false)}
          >
            <button className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all inline-flex items-center gap-1.5 cursor-pointer">
              <span>Services</span>
              <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isServicesDropOpen ? 'rotate-180 text-cyan-400' : ''}`} />
            </button>

            {isServicesDropOpen && (
              <div className="absolute top-full left-0 w-80 bg-[#0c1829] border border-white/10 rounded-2xl shadow-2xl p-3 backdrop-blur-2xl animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="text-[10px] font-bold tracking-wider uppercase text-cyan-400 px-3 py-1.5">
                  Featured Specialties
                </div>
                <div className="space-y-1 mt-1">
                  {(business.detailedServices || []).slice(0, 5).map((srv, idx) => (
                    <a
                      key={idx}
                      href="#services"
                      onClick={() => setIsServicesDropOpen(false)}
                      className="block px-3 py-2.5 rounded-xl hover:bg-white/5 transition-colors group"
                    >
                      <div className="text-xs font-semibold text-white group-hover:text-cyan-300 transition-colors flex items-center justify-between">
                        <span>{srv.title}</span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transform group-hover:translate-x-1 transition-all text-cyan-400" />
                      </div>
                      <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{srv.description}</p>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          <a href="#why-us" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all">
            Why Choose Us
          </a>
          <a href="#workflow" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all">
            Process
          </a>
          <a href="#reviews" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all">
            Reviews
          </a>
          <a href="#faq" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all">
            FAQ
          </a>
        </nav>

        {/* Desktop CTA Action */}
        <div className="hidden lg:flex items-center gap-3">
          {business.phone && (
            <a
              href={`tel:${business.phone}`}
              className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white border border-white/15 hover:border-white/30 rounded-xl transition-all inline-flex items-center gap-2"
            >
              <Phone className="w-3.5 h-3.5 text-cyan-400" />
              <span>{business.phone}</span>
            </a>
          )}

          <button
            onClick={onOpenBooking}
            className="gradient-btn-primary px-5 py-2.5 rounded-xl text-xs font-bold text-white tracking-wide uppercase inline-flex items-center gap-2 cursor-pointer"
          >
            <Calendar className="w-4 h-4" />
            <span>Book Appointment</span>
          </button>
        </div>

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="md:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
          aria-label="Toggle Navigation Menu"
        >
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-[#07101f] border-b border-white/10 px-6 py-6 space-y-4 animate-in slide-in-from-top duration-300">
          <nav className="flex flex-col space-y-3">
            <a
              href="#"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Home
            </a>
            <a
              href="#services"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Our Services
            </a>
            <a
              href="#why-us"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Why Choose Us
            </a>
            <a
              href="#workflow"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Treatment Workflow
            </a>
            <a
              href="#reviews"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Patient Reviews
            </a>
            <a
              href="#faq"
              onClick={() => setIsMobileMenuOpen(false)}
              className="text-sm font-medium text-slate-200 hover:text-white py-1"
            >
              Frequently Asked Questions
            </a>
          </nav>

          <div className="pt-4 border-t border-white/10 space-y-3">
            {business.phone && (
              <a
                href={`tel:${business.phone}`}
                className="w-full py-3 rounded-xl border border-white/20 text-center text-sm font-semibold text-white flex items-center justify-center gap-2"
              >
                <Phone className="w-4 h-4 text-cyan-400" />
                <span>Call {business.phone}</span>
              </a>
            )}

            <button
              onClick={() => {
                setIsMobileMenuOpen(false);
                onOpenBooking();
              }}
              className="w-full gradient-btn-primary py-3 rounded-xl text-center text-sm font-bold text-white flex items-center justify-center gap-2 cursor-pointer"
            >
              <Calendar className="w-4 h-4" />
              <span>Book Appointment Now</span>
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
