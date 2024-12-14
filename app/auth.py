import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
API_KEY_NAME = "X-API-Key"
API_KEY = os.environ["API_API_KEY"]
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header not found"
        )
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key_header
