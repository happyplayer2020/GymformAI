import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function POST(request: NextRequest) {
  try {
    const { userId, email, priceId, billingCycle } = await request.json();

    // Validate input
    if (!userId || !email || !priceId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Create checkout session by calling backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscriptions/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${request.headers.get('authorization')}`,
      },
      body: JSON.stringify({ 
        userId, 
        email, 
        priceId,
        billingCycle: billingCycle || 'monthly'
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create checkout session');
    }

    const { sessionId } = await response.json();

    return NextResponse.json({ sessionId });

  } catch (error) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: 'Failed to create checkout session' },
      { status: 500 }
    );
  }
} 