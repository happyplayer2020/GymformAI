from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.auth import get_current_user
from app.models.user import User
import stripe
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutSessionRequest(BaseModel):
    userId: str
    email: str
    priceId: str
    billingCycle: str = "monthly"

@router.post("/create-checkout-session")
async def create_checkout_session(
    request_data: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription"""
    try:
        # Validate price ID
        if not request_data.priceId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price ID is required"
            )

        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[
                {
                    'price': request_data.priceId,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cancel",
            metadata={
                'user_id': current_user.id,
                'billing_cycle': request_data.billingCycle,
            },
        )
        
        return {"sessionId": checkout_session.id}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Handle successful subscription
            await handle_successful_subscription(session)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            # Handle subscription cancellation
            await handle_subscription_cancellation(subscription)
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )

async def handle_successful_subscription(session):
    """Handle successful subscription"""
    # This would update the user's subscription status in the database
    pass

async def handle_subscription_cancellation(subscription):
    """Handle subscription cancellation"""
    # This would update the user's subscription status in the database
    pass 