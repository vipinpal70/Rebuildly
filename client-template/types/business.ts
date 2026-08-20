export interface ReviewItem {
  author: string;
  rating: number;
  text: string;
  relativeTime: string;
  resultBadge?: string;
  avatarLetter?: string;
}

export interface StatItem {
  number: string;
  label: string;
  highlight?: string;
}

export interface USPItem {
  icon: string;
  title: string;
  description: string;
}

export interface WorkflowItem {
  step: string;
  title: string;
  description: string;
}

export interface FAQItem {
  question: string;
  answer: string;
}

export interface DetailedService {
  title: string;
  category: string;
  description: string;
  features: string[];
}

export interface HeroChip {
  title: string;
  subtitle: string;
  highlight?: string;
}

export interface BusinessData {
  slug: string;
  name: string;
  category: string;
  city: string;
  country: string;
  address?: string;
  phone?: string;
  email?: string;
  website?: string;
  google_rating: number;
  review_count: number;
  google_maps_url?: string;
  tagline: string;
  heroSubtitle?: string;
  badgeText?: string;
  heroImage?: string;
  videoUrl?: string;
  hours?: string;
  emergencyPhone?: string;
  modernization_score?: number;
  preview_url?: string;
  stats: StatItem[];
  usps: USPItem[];
  workflow: WorkflowItem[];
  faqs: FAQItem[];
  services: string[];
  detailedServices: DetailedService[];
  reviews: ReviewItem[];
  heroChips: HeroChip[];
}
