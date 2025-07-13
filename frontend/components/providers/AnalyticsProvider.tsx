'use client';

import { createContext, useContext, useEffect } from 'react';
import mixpanel from 'mixpanel-browser';

interface AnalyticsContextType {
  track: (event: string, properties?: Record<string, any>) => void;
  identify: (userId: string, properties?: Record<string, any>) => void;
  setUserProperties: (properties: Record<string, any>) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

const MIXPANEL_TOKEN = process.env.NEXT_PUBLIC_MIXPANEL_TOKEN;

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (MIXPANEL_TOKEN) {
      mixpanel.init(MIXPANEL_TOKEN, {
        debug: process.env.NODE_ENV === 'development',
        track_pageview: true,
        persistence: 'localStorage',
      });
    }
  }, []);

  const track = (event: string, properties?: Record<string, any>) => {
    if (MIXPANEL_TOKEN) {
      mixpanel.track(event, properties);
    }
  };

  const identify = (userId: string, properties?: Record<string, any>) => {
    if (MIXPANEL_TOKEN) {
      mixpanel.identify(userId);
      if (properties) {
        mixpanel.people.set(properties);
      }
    }
  };

  const setUserProperties = (properties: Record<string, any>) => {
    if (MIXPANEL_TOKEN) {
      mixpanel.people.set(properties);
    }
  };

  const value = {
    track,
    identify,
    setUserProperties,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export function useAnalytics() {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
} 