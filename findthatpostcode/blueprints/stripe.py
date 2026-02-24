from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from findthatpostcode.models import Payment, Subscription, User
from findthatpostcode.settings import STRIPE_SECRET_KEY, STRIPE_SIGNING_SECRET

router = APIRouter(prefix="/stripe")


def get_db():
    """Get database session for subscription management"""
    from sqlmodel import create_engine

    from findthatpostcode.settings import DATABASE_URL

    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session


def get_stripe_client():
    """Get configured Stripe client"""
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


@router.post("/event")
async def stripe_event(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    print(request.headers)
    payload = await request.body()
    print(payload)
    sig_header = request.headers.get("stripe-signature")
    print(sig_header)
    event = None

    stripe.api_key = STRIPE_SECRET_KEY

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_SIGNING_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print("Error parsing payload: {}".format(str(e)))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Error verifying webhook signature: {}".format(str(e)))
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event.type == "customer.subscription.created":
        subscription = event.data.object
        await handle_subscription_created(subscription, db)

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        await handle_subscription_updated(subscription, db)

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        await handle_subscription_deleted(subscription, db)

    elif event.type == "invoice.payment_succeeded":
        invoice = event.data.object
        await handle_payment_succeeded(invoice, db)

    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        await handle_payment_failed(invoice, db)

    elif event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        print("PaymentIntent was successful!")

    elif event.type == "payment_method.attached":
        payment_method = event.data.object
        print("PaymentMethod was attached to a Customer!")

    else:
        print("Unhandled event type {}".format(event.type))

    return {"status": "success"}


async def handle_subscription_created(subscription, db: Session):
    """Handle subscription creation event"""
    print(f"Subscription created: {subscription.id}")

    # Find user by stripe_customer_id
    user = (
        db.query(User).filter(User.stripe_customer_id == subscription.customer).first()
    )

    if user:
        # Create subscription record
        new_subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=subscription.id,
            stripe_price_id=subscription.items.data[0].price.id,
            status=subscription.status,
            current_period_start=datetime.fromtimestamp(
                subscription.current_period_start
            ),
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            cancel_at_period_end=subscription.cancel_at_period_end,
            canceled_at=datetime.fromtimestamp(subscription.canceled_at)
            if subscription.canceled_at
            else None,
        )

        db.add(new_subscription)
        db.commit()
        print(f"Created subscription record for user {user.id}")


async def handle_subscription_updated(subscription, db: Session):
    """Handle subscription update event"""
    print(f"Subscription updated: {subscription.id}")

    # Find subscription by stripe_subscription_id
    db_subscription = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == subscription.id)
        .first()
    )

    if db_subscription:
        # Update subscription record
        db_subscription.status = subscription.status
        db_subscription.current_period_start = datetime.fromtimestamp(
            subscription.current_period_start
        )
        db_subscription.current_period_end = datetime.fromtimestamp(
            subscription.current_period_end
        )
        db_subscription.cancel_at_period_end = subscription.cancel_at_period_end
        db_subscription.canceled_at = (
            datetime.fromtimestamp(subscription.canceled_at)
            if subscription.canceled_at
            else None
        )

        db.commit()
        print(f"Updated subscription record {db_subscription.id}")


async def handle_subscription_deleted(subscription, db: Session):
    """Handle subscription deletion event"""
    print(f"Subscription deleted: {subscription.id}")

    # Find subscription by stripe_subscription_id
    db_subscription = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == subscription.id)
        .first()
    )

    if db_subscription:
        # Mark subscription as canceled
        db_subscription.status = "canceled"
        db_subscription.canceled_at = datetime.now()

        db.commit()
        print(f"Marked subscription {db_subscription.id} as canceled")


async def handle_payment_succeeded(invoice, db: Session):
    """Handle successful payment event"""
    print(f"Payment succeeded for invoice: {invoice.id}")

    # Find subscription by stripe_subscription_id
    subscription = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == invoice.subscription)
        .first()
    )

    if subscription:
        # Create payment record
        payment_intent = invoice.payment_intent

        new_payment = Payment(
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent,
            amount=invoice.amount_paid,
            currency=invoice.currency,
            status="succeeded",
            created_at=datetime.fromtimestamp(invoice.created),
        )

        db.add(new_payment)
        db.commit()
        print(f"Created payment record for subscription {subscription.id}")


async def handle_payment_failed(invoice, db: Session):
    """Handle failed payment event"""
    print(f"Payment failed for invoice: {invoice.id}")

    # Find subscription by stripe_subscription_id
    subscription = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == invoice.subscription)
        .first()
    )

    if subscription:
        # Create failed payment record
        payment_intent = invoice.payment_intent

        new_payment = Payment(
            subscription_id=subscription.id,
            stripe_payment_intent_id=payment_intent,
            amount=invoice.amount_due,
            currency=invoice.currency,
            status="failed",
            created_at=datetime.fromtimestamp(invoice.created),
        )

        db.add(new_payment)
        db.commit()
        print(f"Created failed payment record for subscription {subscription.id}")


@router.post("/create-customer")
async def create_stripe_customer(email: str, db: Session = Depends(get_db)):
    """Create a Stripe customer"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Create customer in Stripe
        customer = stripe.Customer.create(
            email=email, description=f"Customer for {email}"
        )

        # Find or create user
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.stripe_customer_id = customer.id
            db.commit()
            return {"customer_id": customer.id, "user_id": user.id}
        else:
            # Create new user
            new_user = User(
                email=email, password_hash="", stripe_customer_id=customer.id
            )
            db.add(new_user)
            db.commit()

            return {"customer_id": customer.id, "user_id": new_user.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-subscription")
async def create_subscription(
    customer_id: str, price_id: str, db: Session = Depends(get_db)
):
    """Create a Stripe subscription"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Create subscription in Stripe
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str, db: Session = Depends(get_db)):
    """Get subscription details"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Get subscription from Stripe
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Get subscription from database
        db_subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == subscription_id)
            .first()
        )

        return {"stripe_subscription": subscription, "db_subscription": db_subscription}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(subscription_id: str, db: Session = Depends(get_db)):
    """Cancel a subscription"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Cancel subscription in Stripe
        subscription = stripe.Subscription.delete(subscription_id)

        # Update subscription in database
        db_subscription = (
            db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == subscription_id)
            .first()
        )

        if db_subscription:
            db_subscription.status = "canceled"
            db_subscription.canceled_at = datetime.now()
            db.commit()

        return {"status": "canceled", "subscription": subscription}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
