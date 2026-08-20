import React from 'react';
import siteConfig from '../../../public/previews/insight-law.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {
  title: "Insight Law | Custom Web Preview",
  description: "Your property move, handled from offer to completion \u2014 no surprises, no delays",
};

export default function DedicatedPage() {
  return <DynamicClientSite siteConfig={siteConfig as any} />;
}
