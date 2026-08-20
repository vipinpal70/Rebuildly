'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { BusinessData } from '../../../types/business';
import { sampleBusiness } from '../../../data/sampleBusiness';
import { SchemaMarkup } from '../../../components/SchemaMarkup';
import { TopStrip } from '../../../components/TopStrip';
import { Header } from '../../../components/Header';
import { HeroSection } from '../../../components/HeroSection';
import { TrustStrip } from '../../../components/TrustStrip';
import { ServicesSection } from '../../../components/ServicesSection';
import { WhyChooseUs } from '../../../components/WhyChooseUs';
import { WorkflowSection } from '../../../components/WorkflowSection';
import { ReviewCarousel } from '../../../components/ReviewCarousel';
import { FAQSection } from '../../../components/FAQSection';
import { CTASection } from '../../../components/CTASection';
import { Footer } from '../../../components/Footer';
import { BookingModal } from '../../../components/BookingModal';
import { ChatbotWidget } from '../../../components/ChatbotWidget';

export default function PreviewPage() {
  const params = useParams();
  const slug = params?.slug as string;
  const [business, setBusiness] = useState<BusinessData>(sampleBusiness);
  const [isBookingOpen, setIsBookingOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;

    // Attempt to load generated JSON preview config from /previews/[slug].json
    fetch(`/previews/${slug}.json`)
      .then((res) => {
        if (res.ok) return res.json();
        throw new Error('No custom config found');
      })
      .then((customData: Partial<BusinessData>) => {
        setBusiness({
          ...sampleBusiness,
          ...customData,
          slug,
        });
      })
      .catch(() => {
        // Fallback: Format slug into presentable business name using sample structure
        const formattedName = slug
          .split('-')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');

        setBusiness((prev) => ({
          ...prev,
          slug,
          name: formattedName,
          city: prev.city || 'Your City',
          badgeText: `🔥 #1 RATED ${prev.category.toUpperCase()} IN ${formattedName.toUpperCase()}`,
        }));
      })
      .finally(() => setLoading(false));
  }, [slug]);

  return (
    <main className="min-h-screen bg-[#07101f] text-slate-100 selection:bg-cyan-500 selection:text-white relative">
      {/* Top Banner Notice */}
      <div className="bg-gradient-to-r from-blue-700 via-cyan-600 to-indigo-700 text-white text-center py-2 px-4 text-xs font-bold tracking-wide shadow-md flex items-center justify-center gap-2">
        <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
        <span>LIVE MODERNIZED CLIENT PREVIEW DEMO • PREPARED FOR {business.name.toUpperCase()}</span>
      </div>

      <SchemaMarkup business={business} />
      <TopStrip business={business} onOpenBooking={() => setIsBookingOpen(true)} />
      <Header business={business} onOpenBooking={() => setIsBookingOpen(true)} />
      <HeroSection business={business} onOpenBooking={() => setIsBookingOpen(true)} />
      <TrustStrip business={business} />
      <ServicesSection business={business} onOpenBooking={() => setIsBookingOpen(true)} />
      <WhyChooseUs business={business} />
      <WorkflowSection business={business} />
      <ReviewCarousel business={business} />
      <FAQSection business={business} />
      <CTASection business={business} onOpenBooking={() => setIsBookingOpen(true)} />
      <Footer business={business} />

      <BookingModal
        business={business}
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
      />
      <ChatbotWidget business={business} />
    </main>
  );
}
