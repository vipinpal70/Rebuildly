import React from 'react';
import siteConfig from '../../../public/previews/clarity-dental-clinic.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Clarity Dental Clinic | Custom Web Preview",
  description: "Advanced dentistry without the wait",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
