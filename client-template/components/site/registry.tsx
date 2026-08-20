import React from 'react';
import Hero from '../sections/Hero';
import Services from '../sections/Services';
import Faq from '../sections/Faq';
import Cta from '../sections/Cta';
import Reviews from '../sections/Reviews';
import Workflow from '../sections/Workflow';
import { TrustRibbon, Usps } from '../sections/MiscSections';
import { Gallery, Team, LocationMap } from '../sections/RichSections';

// Maps the generator's `section_order` keys to section components. A key with no
// entry is skipped gracefully, so new section types never crash a page.
export const SECTION_REGISTRY: Record<string, React.FC> = {
  hero: Hero,
  trust_ribbon: TrustRibbon,
  services: Services,
  gallery: Gallery,
  usps: Usps,
  team: Team,
  workflow: Workflow,
  reviews: Reviews,
  faqs: Faq,
  location: LocationMap,
  cta: Cta,
};

export const DEFAULT_ORDER = [
  'hero', 'trust_ribbon', 'services', 'gallery',
  'usps', 'team', 'workflow', 'reviews', 'faqs', 'location', 'cta',
];
