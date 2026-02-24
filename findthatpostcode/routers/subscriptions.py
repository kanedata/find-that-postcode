"""Subscription management endpoints"""

from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from findthatpostcode.models import Payment, Subscription, User
from findthatpostcode.settings import STRIPE_SECRET_KEY

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


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


@router.get("/user/{user_id}")
async def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    """Get all subscriptions for a user"""
    try:
        # Get user with their subscriptions
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get active subscriptions
        active_subscriptions = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.status == "active")
            .all()
        )

        # Get all subscriptions
        all_subscriptions = (
            db.query(Subscription).filter(Subscription.user_id == user_id).all()
        )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "stripe_customer_id": user.stripe_customer_id,
            },
            "active_subscriptions": active_subscriptions,
            "all_subscriptions": all_subscriptions,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{subscription_id}")
async def get_subscription_details(subscription_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a subscription"""
    try:
        # Get subscription with payments
        subscription = (
            db.query(Subscription).filter(Subscription.id == subscription_id).first()
        )

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Get payments for this subscription
        payments = (
            db.query(Payment)
            .filter(Payment.subscription_id == subscription_id)
            .order_by(Payment.created_at.desc())
            .all()
        )

        # Get user information
        user = db.query(User).filter(User.id == subscription.user_id).first()

        return {
            "subscription": subscription,
            "user": {"id": user.id, "email": user.email},
            "payments": payments,
            "payment_count": len(payments),
            "total_amount_paid": sum(
                p.amount for p in payments if p.status == "succeeded"
            ),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-checkout-session")
async def create_checkout_session(
    user_id: int,
    price_id: str,
    success_url: str,
    cancel_url: str,
    db: Session = Depends(get_db),
):
    """Create a Stripe checkout session for subscription"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Get user
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email, description=f"Customer for {user.email}"
            )
            user.stripe_customer_id = customer.id
            db.commit()

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": str(user_id)},
        )

        return {"session_id": checkout_session.id, "url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cancel/{subscription_id}")
async def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Cancel a subscription"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Get subscription from database
        subscription = (
            db.query(Subscription).filter(Subscription.id == subscription_id).first()
        )

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Cancel subscription in Stripe
        stripe_subscription = stripe.Subscription.delete(
            subscription.stripe_subscription_id
        )

        # Update subscription in database
        subscription.status = "canceled"
        subscription.canceled_at = datetime.now()
        db.commit()

        return {
            "status": "success",
            "subscription_id": subscription.id,
            "stripe_status": stripe_subscription.status,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reactivate/{subscription_id}")
async def reactivate_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Reactivate a canceled subscription"""
    try:
        stripe.api_key = STRIPE_SECRET_KEY

        # Get subscription from database
        subscription = (
            db.query(Subscription).filter(Subscription.id == subscription_id).first()
        )

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        if subscription.status != "canceled":
            raise HTTPException(status_code=400, detail="Subscription is not canceled")

        # Reactivate subscription in Stripe
        stripe_subscription = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )

        if stripe_subscription.status == "canceled":
            # Create a new subscription with the same price
            new_subscription = stripe.Subscription.create(
                customer=stripe_subscription.customer,
                items=[{"price": subscription.stripe_price_id}],
                backdate_start_date=datetime.now().timestamp(),
            )

            # Update database record
            subscription.stripe_subscription_id = new_subscription.id
            subscription.status = new_subscription.status
            subscription.current_period_start = datetime.fromtimestamp(
                new_subscription.current_period_start
            )
            subscription.current_period_end = datetime.fromtimestamp(
                new_subscription.current_period_end
            )
            subscription.canceled_at = None
            subscription.cancel_at_period_end = new_subscription.cancel_at_period_end
            db.commit()

            return {
                "status": "success",
                "new_subscription_id": new_subscription.id,
                "subscription": subscription,
            }
        else:
            # Just update the status if it's not actually canceled in Stripe
            subscription.status = stripe_subscription.status
            subscription.canceled_at = None
            db.commit()

            return {"status": "success", "subscription": subscription}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}/payments")
async def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    """Get all payments for a user"""
    try:
        # Get user's subscriptions
        subscriptions = (
            db.query(Subscription).filter(Subscription.user_id == user_id).all()
        )

        if not subscriptions:
            return {"payments": [], "total_amount": 0}

        # Get all payments for these subscriptions
        subscription_ids = [sub.id for sub in subscriptions]

        payments = (
            db.query(Payment)
            .filter(Payment.subscription_id.in_(subscription_ids))
            .order_by(Payment.created_at.desc())
            .all()
        )

        return {
            "payments": payments,
            "total_amount": sum(p.amount for p in payments if p.status == "succeeded"),
            "successful_payments": len(
                [p for p in payments if p.status == "succeeded"]
            ),
            "failed_payments": len([p for p in payments if p.status == "failed"]),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_subscription_status(user_id: int, db: Session = Depends(get_db)):
    """Get subscription status for a user"""
    try:
        # Check if user has any active subscriptions
        active_subscriptions = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.status == "active")
            .count()
        )

        # Get user info
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": user_id,
            "has_active_subscription": active_subscriptions > 0,
            "stripe_customer_id": user.stripe_customer_id,
            "subscription_count": active_subscriptions,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
