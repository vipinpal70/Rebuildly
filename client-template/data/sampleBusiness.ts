import { BusinessData } from '../types/business';

export const sampleBusiness: BusinessData = {
  slug: 'deansgate-dental-studio',
  name: 'Deansgate Dental Studio',
  category: 'Dentist & Cosmetic Clinic',
  city: 'Manchester',
  country: 'UK',
  address: '124 Deansgate, Manchester M3 2BW, United Kingdom',
  phone: '+44 161 834 1234',
  emergencyPhone: '+44 161 999 8877',
  email: 'info@deansgatedentalstudio.co.uk',
  website: 'https://deansgatedentalstudio.co.uk',
  google_rating: 4.9,
  review_count: 184,
  tagline: 'Manchester’s Premier Cosmetic Dentistry & Dental Implant Specialists',
  badgeText: '🔥 #1 RATED CLINICAL DENTAL PRACTICE IN MANCHESTER',
  heroSubtitle: 'Combining state-of-the-art 3D digital dentistry with gentle, painless care for a radiant smile that lasts a lifetime.',
  hours: 'Mon - Fri: 8:00 AM - 6:00 PM | Sat: 9:00 AM - 2:00 PM',
  modernization_score: 88,
  preview_url: 'http://localhost:3009/preview/deansgate-dental-studio',
  
  stats: [
    { number: '99.8%', label: 'PATIENT SATISFACTION RATE' },
    { number: '15,000+', label: 'SMILES TRANSFORMED' },
    { number: '24/7', label: 'AI ASSISTED APPOINTMENTS' },
    { number: '0 Min', label: 'AVERAGE WAITING ROOM TIME' }
  ],

  heroChips: [
    { title: '99.8% Precision', subtitle: 'Guided 3D Implant Placement' },
    { title: '4.9 ★ Rating', subtitle: '184+ Verified Google Reviews' }
  ],

  usps: [
    {
      icon: 'sparkles',
      title: 'Digital 3D Smile Design',
      description: 'Preview your exact smile transformation on a 3D digital model before treatment even begins.'
    },
    {
      icon: 'clock',
      title: '24/7 Instant Online Booking',
      description: 'No waiting on hold. Reserve your appointment in under 60 seconds with real-time slot sync.'
    },
    {
      icon: 'shield',
      title: 'Painless & Gentle Guarantee',
      description: 'State-of-the-art needle-free sedation and gentle care protocols for anxious patients.'
    },
    {
      icon: 'zap',
      title: 'Same-Day Emergency Relief',
      description: 'Dedicated priority slots reserved every day to relieve acute pain and dental emergencies immediately.'
    },
    {
      icon: 'award',
      title: '10-Year Comprehensive Warranty',
      description: 'We back all dental implants, veneers, and full-mouth restorations with a written guarantee.'
    },
    {
      icon: 'heart',
      title: '0% Interest Financing',
      description: 'Flexible payment plans up to 24 months to make world-class cosmetic dentistry affordable.'
    }
  ],

  workflow: [
    {
      step: '01',
      title: 'Book Consultation Online',
      description: 'Choose your preferred date and service instantly through our 24/7 AI Receptionist system.'
    },
    {
      step: '02',
      title: '3D Scan & Smile Simulation',
      description: 'Visit our Manchester clinic for a comfortable, non-invasive 3D intraoral digital scan.'
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
  ],

  faqs: [
    {
      question: 'How do I book an emergency appointment for dental pain?',
      answer: 'You can book an immediate emergency slot 24/7 using our live online receptionist or by calling our priority line. We reserve same-day emergency slots daily.'
    },
    {
      question: 'Are cosmetic treatments like Invisalign and Veneers painful?',
      answer: 'Not at all. We utilize non-invasive digital scanning and gentle sedation options to ensure a completely comfortable, pain-free experience.'
    },
    {
      question: 'Do you offer flexible payment plans for dental implants?',
      answer: 'Yes! We offer 0% APR financing spread across 6, 12, or 24 months so you can receive immediate treatment with manageable monthly payments.'
    },
    {
      question: 'What makes digital 3D dentistry superior to traditional molds?',
      answer: 'Digital 3D intraoral scans take under 2 minutes, eliminate uncomfortable impression putty, and deliver 10x greater precision for long-lasting results.'
    }
  ],

  services: [
    'Cosmetic Dentistry & Porcelain Veneers',
    'Dental Implants & All-on-X Restorations',
    'Invisalign Clear Aligners',
    'Same-Day Emergency Dental Care',
    'Laser Teeth Whitening',
    'Composite Smile Bonding'
  ],

  detailedServices: [
    {
      title: 'Cosmetic Dentistry & Porcelain Veneers',
      category: 'COSMETIC',
      description: 'Ultra-thin, custom-crafted porcelain veneers designed to fix gaps, chips, and discoloration for a red-carpet smile.',
      features: ['Digital Smile Preview', 'Stain-Resistant Porcelain', 'Minimal Tooth Preparation', '10-Year Warranty']
    },
    {
      title: 'Dental Implants & Full-Arch Restorations',
      category: 'RESTORATIVE',
      description: 'Permanent, natural-feeling tooth replacement using medical-grade titanium implants and custom zirconia crowns.',
      features: ['3D CBCT Surgical Precision', 'Permanent Fixing', 'Looks & Feels Natural', '0% APR Financing Available']
    },
    {
      title: 'Invisalign® Clear Aligners',
      category: 'ORTHODONTICS',
      description: 'Straighten your teeth discreetly with virtually invisible, removable aligners engineered for comfortable daily wear.',
      features: ['No Metal Brackets', 'Removable for Eating', '3D Progress Simulation', 'Accelerated Treatment Option']
    },
    {
      title: 'Same-Day Emergency Care',
      category: 'EMERGENCY',
      description: 'Immediate relief for severe toothaches, broken crowns, dental trauma, and sudden infections.',
      features: ['Same-Day Guarantee', 'Pain Relief Protocol', 'On-Site X-Rays', 'Direct Tele-Consultation']
    },
    {
      title: 'Laser Teeth Whitening',
      category: 'COSMETIC',
      description: 'Brighten your teeth up to 8 shades in a single 45-minute in-office treatment with zero enamel sensitivity.',
      features: ['In-Office 45 Minute Visit', 'Zero Sensitivity Formula', 'Includes Take-Home Touch Up', 'Instant Dramatic Results']
    },
    {
      title: 'Composite Smile Bonding',
      category: 'COSMETIC',
      description: 'Artistic single-visit composite reshaping to correct minor chips, gaps, and uneven tooth edges naturally.',
      features: ['Completed in 1 Visit', 'No Drilling Required', 'Reversible Treatment', 'Budget-Friendly Option']
    }
  ],

  reviews: [
    {
      author: 'Eleanor Vance',
      rating: 5,
      text: 'Absolutely transformed my smile before my wedding! The 3D digital preview showed me exactly what to expect. The team made me feel completely comfortable and the results are incredible.',
      relativeTime: '2 weeks ago',
      resultBadge: 'Painless Veneer Transformation',
      avatarLetter: 'E'
    },
    {
      author: 'Marcus Sterling',
      rating: 5,
      text: 'Pain-free dental implants! Professional, state-of-the-art facility right in central Manchester. The 24/7 online booking made scheduling so simple.',
      relativeTime: '1 month ago',
      resultBadge: 'Implant Restoration',
      avatarLetter: 'M'
    },
    {
      author: 'Chloe Bennet',
      rating: 5,
      text: 'The best dental experience I have ever had. Gentle staff, instant booking, and flawless Invisalign results in under 6 months!',
      relativeTime: '3 months ago',
      resultBadge: 'Invisalign Treatment',
      avatarLetter: 'C'
    }
  ]
};
