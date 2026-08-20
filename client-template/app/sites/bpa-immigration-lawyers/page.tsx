import React from 'react';
import siteConfig from '../../../public/previews/bpa-immigration-lawyers.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "BPA Immigration Lawyers | Custom Web Preview",
  description: "Immigration cases that turn on detail. We handle yours like it's the only one we have.",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
