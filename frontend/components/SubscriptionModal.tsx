'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Crown, Check, Loader2, Zap, Infinity, Calendar } from 'lucide-react';
import { useSupabase } from '@/components/providers/SupabaseProvider';
import { useAnalytics } from '@/components/providers/AnalyticsProvider';
import { loadStripe } from '@stripe/stripe-js';
import toast from 'react-hot-toast';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export function SubscriptionModal({ isOpen, onClose }: SubscriptionModalProps) {
  const { user } = useSupabase();
  const { track } = useAnalytics();
  const [isLoading, setIsLoading] = useState(false);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const pricing = {
    monthly: {
      price: 9.99,
      priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_MONTHLY,
      period: 'month',
      savings: null
    },
    yearly: {
      price: 99.99, // Assuming €99.99/year (2 months free)
      priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_YEARLY,
      period: 'year',
      savings: 'Save 17%'
    }
  };

  const currentPlan = pricing[billingCycle];

  const handleUpgrade = async () => {
    if (!user) {
      toast.error('Please sign in to upgrade');
      return;
    }

    if (!currentPlan.priceId) {
      toast.error('Pricing not configured');
      return;
    }

    setIsLoading(true);

    try {
      track('subscription_upgrade_started', { billing_cycle: billingCycle });

      // Create Stripe checkout session
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: user.id,
          email: user.email,
          priceId: currentPlan.priceId,
          billingCycle: billingCycle
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { sessionId } = await response.json();

      // Redirect to Stripe checkout
      const stripe = await stripePromise;
      if (stripe) {
        const { error } = await stripe.redirectToCheckout({
          sessionId,
        });

        if (error) {
          throw error;
        }
      }
    } catch (error: any) {
      console.error('Upgrade error:', error);
      toast.error('Failed to start upgrade process');
      track('subscription_upgrade_failed', { error: error.message, billing_cycle: billingCycle });
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    'Unlimited video analyses',
    'Advanced form insights',
    'Progress tracking',
    'Priority support',
    'Export analysis reports',
    'Custom exercise library',
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="relative bg-white rounded-xl shadow-xl w-full max-w-lg mx-4"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-warning-100 rounded-lg flex items-center justify-center">
                  <Crown className="w-6 h-6 text-warning-600" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    Upgrade to Pro
                  </h2>
                  <p className="text-sm text-gray-500">
                    Unlock unlimited analyses and advanced features
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Billing Cycle Toggle */}
              <div className="flex items-center justify-center mb-6">
                <div className="bg-gray-100 rounded-lg p-1 flex">
                  <button
                    onClick={() => setBillingCycle('monthly')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      billingCycle === 'monthly'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Monthly
                  </button>
                  <button
                    onClick={() => setBillingCycle('yearly')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors relative ${
                      billingCycle === 'yearly'
                        ? 'bg-white text-gray-900 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Yearly
                    {pricing.yearly.savings && (
                      <span className="absolute -top-2 -right-2 bg-success-500 text-white text-xs px-2 py-1 rounded-full">
                        {pricing.yearly.savings}
                      </span>
                    )}
                  </button>
                </div>
              </div>

              {/* Pricing */}
              <div className="text-center mb-6">
                <div className="flex items-center justify-center space-x-2 mb-2">
                  <span className="text-4xl font-bold text-gray-900">€{currentPlan.price}</span>
                  <span className="text-gray-500">/{currentPlan.period}</span>
                </div>
                {billingCycle === 'yearly' && (
                  <p className="text-sm text-gray-600 mb-2">
                    €{(currentPlan.price / 12).toFixed(2)}/month when billed annually
                  </p>
                )}
                <p className="text-sm text-gray-600">
                  Cancel anytime • No setup fees
                </p>
              </div>

              {/* Features */}
              <div className="space-y-3 mb-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center space-x-3"
                  >
                    <div className="w-5 h-5 bg-success-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-success-600" />
                    </div>
                    <span className="text-gray-700">{feature}</span>
                  </motion.div>
                ))}
              </div>

              {/* Comparison */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-medium text-gray-900 mb-3">Plan Comparison</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-700 mb-2">Free Plan</p>
                    <div className="space-y-1 text-gray-600">
                      <p>• 3 analyses per day</p>
                      <p>• Basic form feedback</p>
                      <p>• Standard support</p>
                    </div>
                  </div>
                  <div>
                    <p className="font-medium text-primary-700 mb-2">Pro Plan</p>
                    <div className="space-y-1 text-gray-600">
                      <p>• <Infinity className="w-3 h-3 inline" /> Unlimited analyses</p>
                      <p>• Advanced insights</p>
                      <p>• Priority support</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={handleUpgrade}
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    <span>
                      Upgrade to Pro - €{currentPlan.price}/{currentPlan.period}
                    </span>
                  </>
                )}
              </button>

              {/* Security Note */}
              <p className="text-xs text-gray-500 text-center mt-4">
                Secure payment powered by Stripe. Your data is protected and encrypted.
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
} 