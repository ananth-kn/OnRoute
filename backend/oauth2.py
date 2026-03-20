from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse
from fastapi import Depends, HTTPException, status, Request
from database import get_db
import schemas, models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRATION_TIME_IN_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    encode_data = data.copy()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=1)
    encode_data.update({"exp" : expiration_time})
    token = jwt.encode(encode_data, key= SECRET_KEY, algorithm= ALGORITHM)
    return token

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    data.update({"exp": expire, "type": "refresh"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise credentials_exception
        token = schemas.TokenData(tenant_id=tenant_id)
    except JWTError:
        raise credentials_exception
    return token

async def get_current_tenant(request: Request, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    token = verify_access_token(token, credentials_exception)
    tenant = (await db.execute(select(models.Tenant).where(models.Tenant.id == token.tenant_id))).scalars().first()
    if not tenant:
        raise credentials_exception
    return tenant