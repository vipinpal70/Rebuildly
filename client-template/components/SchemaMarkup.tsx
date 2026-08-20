import React from 'react';
import { BusinessData } from '../types/business';

interface SchemaMarkupProps {
  business: BusinessData;
}

export const SchemaMarkup: React.FC<SchemaMarkupProps> = ({ business }) => {
  const schemaData = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: business.name,
    description: business.tagline || `Top-rated ${business.category} in ${business.city}, ${business.country}.`,
    address: {
      '@type': 'PostalAddress',
      streetAddress: business.address || `${business.city}, ${business.country}`,
      addressLocality: business.city,
      addressCountry: business.country,
    },
    telephone: business.phone || '',
    url: business.website || '',
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: business.google_rating,
      reviewCount: business.review_count,
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }}
    />
  );
};
