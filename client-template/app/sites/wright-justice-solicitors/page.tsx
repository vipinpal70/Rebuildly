import React from 'react';
import siteConfig from '../../../public/previews/wright-justice-solicitors.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Wright Justice Solicitors | Custom Web Preview",
  description: "Your immigration case understood. Your family's future protected.",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
