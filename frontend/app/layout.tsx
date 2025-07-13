import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from 'react-hot-toast';
import { SupabaseProvider } from '@/components/providers/SupabaseProvider';
import { AnalyticsProvider } from '@/components/providers/AnalyticsProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GymformAI - AI-Powered Fitness Form Analysis',
  description: 'Analyze your workout form with AI. Get instant feedback on your exercise technique, rep counting, and personalized corrections.',
  keywords: 'fitness, AI, form analysis, workout, exercise, pose estimation',
  authors: [{ name: 'GymformAI Team' }],
  creator: 'GymformAI',
  publisher: 'GymformAI',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'GymformAI - AI-Powered Fitness Form Analysis',
    description: 'Analyze your workout form with AI. Get instant feedback on your exercise technique, rep counting, and personalized corrections.',
    url: '/',
    siteName: 'GymformAI',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'GymformAI - AI-Powered Fitness Form Analysis',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GymformAI - AI-Powered Fitness Form Analysis',
    description: 'Analyze your workout form with AI. Get instant feedback on your exercise technique, rep counting, and personalized corrections.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full`}>
        <SupabaseProvider>
          <AnalyticsProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#22c55e',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </AnalyticsProvider>
        </SupabaseProvider>
      </body>
    </html>
  );
} 