import os
import stripe

# Fetch the key from the environment
stripe.api_key = os.getenv("STRIPE_TEST_KEY")

def create_checkout_session(tenant_id: int, plan_id: int, price_id: str):
    """
    Creates a Stripe Checkout Session for a subscription.
    Passes tenant_id and plan_id in the metadata for the webhook handler.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        # In a real app, these would be absolute URLs pointing to your frontend
        success_url='http://localhost:8000/success',
        cancel_url='http://localhost:8000/cancel',
        metadata={
            'tenant_id': str(tenant_id),
            'plan_id': str(plan_id)
        }
    )
    return session
