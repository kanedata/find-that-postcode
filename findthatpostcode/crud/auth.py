from passlib.context import CryptContext
from sqlmodel import Session, select

from findthatpostcode.models import User


def verify_password(
    pwd_context: CryptContext, plain_password: str, hashed_password: str
):
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(pwd_context: CryptContext, password: str):
    """Hash a password for storing"""
    return pwd_context.hash(password)


def get_user(db: Session, email: str):
    """Get user by email"""
    return db.exec(select(User).where(User.email == email)).first()


def authenticate_user(
    pwd_context: CryptContext, db: Session, email: str, password: str
):
    """Authenticate user"""
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(pwd_context, password, user.password_hash):
        return False
    return user


def create_super_user(
    pwd_context: CryptContext, db: Session, email: str, password: str
):
    """Create a super user"""
    print(email)
    print(password)
    hashed_password = get_password_hash(pwd_context, password)
    super_user = User(email=email, password_hash=hashed_password)
    db.add(super_user)
    db.commit()
    db.refresh(super_user)
    return super_user
