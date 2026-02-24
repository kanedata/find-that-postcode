"""Subscription dashboard blueprint"""

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from findthatpostcode.models import APIKey, Payment, Subscription, User
from findthatpostcode.utils import templates

router = APIRouter()


def get_db():
    """Get database session"""
    from sqlmodel import create_engine

    from findthatpostcode.settings import DATABASE_URL

    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session


@router.get("/subscription-dashboard")
async def subscription_dashboard(request: Request, db: Session = Depends(get_db)):
    """Subscription dashboard page"""
    # Check if user is logged in (in a real app, this would use proper authentication)
    # For now, we'll use a simple check
    user_id = request.cookies.get("user_id")

    if user_id:
        # Get user information
        user = db.query(User).filter(User.id == int(user_id)).first()

        if user:
            # Get active subscriptions
            active_subscriptions = (
                db.query(Subscription)
                .filter(
                    Subscription.user_id == user.id, Subscription.status == "active"
                )
                .all()
            )

            # Get all subscriptions
            all_subscriptions = (
                db.query(Subscription).filter(Subscription.user_id == user.id).all()
            )

            # Get payments
            if all_subscriptions:
                subscription_ids = [sub.id for sub in all_subscriptions]
                payments = (
                    db.query(Payment)
                    .filter(Payment.subscription_id.in_(subscription_ids))
                    .order_by(Payment.created_at.desc())
                    .all()
                )

                successful_payments = len(
                    [p for p in payments if p.status == "succeeded"]
                )
                failed_payments = len([p for p in payments if p.status == "failed"])
                total_amount_paid = sum(
                    p.amount for p in payments if p.status == "succeeded"
                )
            else:
                payments = []
                successful_payments = 0
                failed_payments = 0
                total_amount_paid = 0

            # Get API keys
            api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()

            return templates.TemplateResponse(
                request=request,
                name="subscription_dashboard.html.j2",
                context={
                    "user": user,
                    "active_subscriptions": active_subscriptions,
                    "all_subscriptions": all_subscriptions,
                    "payments": payments,
                    "successful_payments": successful_payments,
                    "failed_payments": failed_payments,
                    "total_amount_paid": total_amount_paid,
                    "api_keys": api_keys,
                },
                media_type="text/html",
            )

    # If not logged in, redirect to login
    return templates.TemplateResponse(
        request=request,
        name="login.html.j2",
        context={"error": "Please login to access your subscription dashboard"},
        media_type="text/html",
    )


@router.get("/login")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse(
        request=request, name="login.html.j2", context={}, media_type="text/html"
    )


@router.get("/register")
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse(
        request=request, name="register.html.j2", context={}, media_type="text/html"
    )


@router.get("/forgot-password")
async def forgot_password_page(request: Request):
    """Forgot password page"""
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html.j2",
        context={},
        media_type="text/html",
    )
