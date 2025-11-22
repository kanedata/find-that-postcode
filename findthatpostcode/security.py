from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_scheme = APIKeyHeader(name="X-API-KEY", auto_error=False)


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
