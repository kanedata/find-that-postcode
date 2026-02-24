import datetime
from http import HTTPStatus
from typing import Annotated, Any, AsyncGenerator, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi_csrf_protect import CsrfProtect
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from sqlmodel import Session, or_, select
from starlette_session.backends import _dumps, _loads
from starlette_session.interfaces import ISessionBackend

from findthatpostcode.models import UserSession
from findthatpostcode.settings import SECRET_KEY

api_key_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_api_key(api_key: str = Depends(api_key_scheme)):
    VALID_API_KEYS = {
        "your-secret-api-key-1",
        "your-secret-api-key-2",
    }  # Replace with your actual keys
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_password_context() -> AsyncGenerator[CryptContext, None]:
    yield password_context


PwdContextDep = Annotated[CryptContext, Depends(get_password_context)]


class DBSessionBackend(ISessionBackend):
    def __init__(self, db: Session):
        self.db = db

    async def get(self, key: str, **kwargs: dict) -> Optional[dict]:
        value = self.db.exec(
            select(UserSession).where(
                UserSession.session_key == key,
                or_(
                    UserSession.expire_date == None,  # noqa: E711
                    UserSession.expire_date  # pyright: ignore[reportOptionalOperand]
                    > datetime.datetime.now(datetime.timezone.utc),
                ),
            )
        ).first()
        return _loads(value.session_data) if value else None

    async def set(
        self, key: str, value: dict, exp: Optional[int] = None, **kwargs: dict
    ) -> Optional[str]:
        session_data = _dumps(value)

        # convert exp to datetime from seconds
        expire_date = (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=exp)
            if exp
            else None
        )
        user_session = self.db.exec(
            select(UserSession).where(UserSession.session_key == key)
        ).first()
        if user_session:
            user_session.session_data = session_data
            user_session.expire_date = expire_date
        else:
            user_session = UserSession(
                session_key=key, session_data=session_data, expire_date=expire_date
            )
        self.db.add(user_session)
        self.db.commit()
        return None

    async def delete(self, key: str, **kwargs: dict) -> Any:
        user_session = self.db.exec(
            select(UserSession).where(UserSession.session_key == key)
        ).first()
        if user_session:
            self.db.delete(user_session)
            self.db.commit()


class CsrfSettings(BaseSettings):
    secret_key: str = SECRET_KEY
    cookie_samesite: str = "none"
    cookie_secure: bool = True
    token_location: str = "body"
    token_key: str = "csrf_token"


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
