import React from 'react';
import siteConfig from '../../../public/previews/avalon-care-dental-practice.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Avalon Care Dental Practice | Custom Web Preview",
  description: "Dentistry that fits your life, not your schedule",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
