import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import './globals.css';

const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Client Modernization Website | Top Rated Local Business',
  description: 'Experience premium care, instant online booking, and 24/7 AI receptionist support.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${jakarta.className} antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
