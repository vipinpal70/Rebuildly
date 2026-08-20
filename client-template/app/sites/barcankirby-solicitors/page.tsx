import React from 'react';
import siteConfig from '../../../public/previews/barcankirby-solicitors.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Barcan+Kirby Solicitors | Custom Web Preview",
  description: "When life fractures, clarity matters more than speed",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
