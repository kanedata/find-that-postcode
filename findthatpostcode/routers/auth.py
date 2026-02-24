"""Authentication endpoints for user management"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlmodel import Session

from findthatpostcode.models import APIKey, User
from findthatpostcode.settings import SECRET_KEY

router = APIRouter(prefix="/auth", tags=["Authentication"])


# @router.post("/register", response_model=UserResponse)
# async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     """Register a new user"""
#     # Check if user already exists
#     existing_user = get_user(db, user_data.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # Create new user
#     hashed_password = get_password_hash(user_data.password)
#     new_user = User(email=user_data.email, password_hash=hashed_password)

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return UserResponse(
#         id=new_user.id,
#         email=new_user.email,
#         stripe_customer_id=new_user.stripe_customer_id,
#     )


# @router.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
# ):
#     """Login and get access token"""
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )

#     return {"access_token": access_token, "token_type": "bearer"}


# @router.get("/me", response_model=UserResponse)
# async def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
#     """Get current user information"""
#     return UserResponse(
#         id=current_user.id,
#         email=current_user.email,
#         stripe_customer_id=current_user.stripe_customer_id,
#     )


# @router.post("/api-key")
# async def create_api_key(
#     current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     """Create an API key for the current user"""
#     import secrets

#     # Generate a random API key
#     api_key = secrets.token_urlsafe(32)

#     # Create API key record
#     new_api_key = APIKey(key=api_key, user_id=current_user.id)
#     db.add(new_api_key)
#     db.commit()

#     return {"api_key": api_key}


# @router.get("/api-keys")
# async def get_api_keys(
#     current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
# ):
#     """Get all API keys for the current user"""
#     api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

#     return {
#         "api_keys": [
#             {
#                 "id": key.id,
#                 "created_at": "N/A",  # Would need to add created_at field to model
#                 "last_used": "N/A",
#             }
#             for key in api_keys
#         ]
#     }


# @router.delete("/api-key/{key_id}")
# async def delete_api_key(
#     key_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Delete an API key"""
#     api_key = (
#         db.query(APIKey)
#         .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
#         .first()
#     )

#     if not api_key:
#         raise HTTPException(status_code=404, detail="API key not found")

#     db.delete(api_key)
#     db.commit()

#     return {"status": "success", "message": "API key deleted"}


# @router.post("/change-password")
# async def change_password(
#     current_password: str,
#     new_password: str,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Change user password"""
#     # Verify current password
#     if not verify_password(current_password, current_user.password_hash):
#         raise HTTPException(status_code=400, detail="Current password is incorrect")

#     # Check if new password is different
#     if current_password == new_password:
#         raise HTTPException(
#             status_code=400,
#             detail="New password must be different from current password",
#         )

#     # Update password
#     current_user.password_hash = get_password_hash(new_password)
#     db.commit()

#     return {"status": "success", "message": "Password changed successfully"}


# @router.post("/forgot-password")
# async def forgot_password(email: str, db: Session = Depends(get_db)):
#     """Initiate password reset process"""
#     # In a real implementation, this would send an email with a reset link
#     # For now, we'll just check if the user exists
#     user = get_user(db, email)
#     if not user:
#         # Don't reveal that the user doesn't exist for security reasons
#         return {
#             "status": "success",
#             "message": "If this email exists, a password reset link has been sent",
#         }

#     # In a real implementation, generate a reset token and send email
#     # For now, just return success
#     return {
#         "status": "success",
#         "message": "If this email exists, a password reset link has been sent",
#     }
