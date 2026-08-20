import React from 'react';
import siteConfig from '../../../public/previews/the-temple-practice.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "The Temple Practice | Custom Web Preview",
  description: "Dentistry that feels like it's made for you, not the other way around",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
