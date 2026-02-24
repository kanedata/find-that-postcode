from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password_hash: str
    stripe_customer_id: Optional[str] = Field(default=None)

    # Relationships
    subscriptions: list["Subscription"] = Relationship(back_populates="user")
    api_keys: list["APIKey"] = Relationship(back_populates="user")


class APIKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str
    user_id: int | None = Field(default=None, foreign_key="user.id")

    # Relationships
    user: Optional[User] = Relationship(back_populates="api_keys")


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    stripe_subscription_id: str
    stripe_price_id: str
    status: str  # active, canceled, past_due, etc.
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = Field(default=False)
    canceled_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="subscriptions")
    payments: list["Payment"] = Relationship(back_populates="subscription")


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subscription_id: int = Field(foreign_key="subscription.id")
    stripe_payment_intent_id: str
    amount: int  # in cents/pence
    currency: str
    status: str  # succeeded, failed, etc.
    created_at: datetime

    # Relationships
    subscription: Subscription = Relationship(back_populates="payments")


class UserSession(SQLModel, table=True):
    session_key: str = Field(primary_key=True)
    session_data: bytes  # Serialized session data
    expire_date: Optional[datetime] = Field(default=None)
