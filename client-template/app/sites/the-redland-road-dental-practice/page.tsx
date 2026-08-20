import React from 'react';
import siteConfig from '../../../public/previews/the-redland-road-dental-practice.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "The Redland Road Dental Practice | Custom Web Preview",
  description: "Regular check-ups that actually fit your life",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
