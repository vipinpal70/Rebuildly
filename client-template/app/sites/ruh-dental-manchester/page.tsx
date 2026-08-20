import React from 'react';
import siteConfig from '../../../public/previews/ruh-dental-manchester.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Ruh Dental - Manchester | Custom Web Preview",
  description: "Invisible braces. Visible results. Fast.",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
