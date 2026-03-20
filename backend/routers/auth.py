from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
import schemas, models, utils, oauth2
from database import get_db
from config import settings
from fastapi.templating import Jinja2Templates
import secrets
from datetime import datetime, timedelta, timezone
from config import conf, r
import utils
from fastapi_mail import MessageSchema, FastMail
import redis.asyncio as redis
from oauth2 import get_current_tenant
from config import limiter

templates = Jinja2Templates(directory="../frontend")

router = APIRouter(prefix= "/auth", tags=['Auth'])

@router.get("/login")
async def driver_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/login")
@limiter.limit("10/minute")
async def tenant_login(request: Request, response: Response, credentials: OAuth2PasswordRequestForm = Depends(), db : AsyncSession = Depends(get_db)):
    tenant = (await db.execute(select(models.Tenant).where(models.Tenant.email == credentials.username))).scalar()
    if not tenant:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not utils.verify(credentials.password, tenant.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = oauth2.create_access_token({"tenant_id":tenant.id})
    refresh_token = oauth2.create_refresh_token({"tenant_id":tenant.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", secure=False)
    return {"message": "ok"}

@router.post("/refresh")
@limiter.limit("10/minute")
async def tenant_login(request: Request, response: Response, db : AsyncSession = Depends(get_db)):
    exception = HTTPException(status_code=401, detail="Invalid token! Login to continue")
    token = request.cookies.get("refresh_token")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return RedirectResponse(url="/auth/login")
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        return RedirectResponse(url="/auth/login")
    tenant = (await db.execute(select(models.Tenant).where(models.Tenant.id == tenant_id))).scalars().first()
    if not tenant:
        return RedirectResponse(url="/auth/login")
    access_token = oauth2.create_access_token({"tenant_id":tenant.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax", secure=False)
    return access_token

@router.post("/logout")
async def tenant_logout(response: Response, tenant: dict= Depends(get_current_tenant)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

@router.post("/otp")
@limiter.limit("3/minute")
async def sendotp(request: Request,
    email: schemas.Email, db: AsyncSession = Depends(get_db)):
    num = (await r.get(f"otp@{email.email}"))
    num = 1 if not num else int(num)+1
    print(num)
    if num>3:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later") 
    await r.set(f"otp@{email.email}", num, ex=300)

    otp = str(secrets.randbelow(10**6)).zfill(6)
    hashed_otp = utils.hash(otp)
    new_otp = models.OTP(email=email.email, hashed_otp = hashed_otp)
    db.add(new_otp)
    await db.flush()
    expires_at = new_otp.created_at + timedelta(minutes=5)
    new_otp.expires_at = expires_at
    await db.commit()
    try:
        message = MessageSchema(subject="Your OTP code for verification",recipients=[email.email],
        body=
        f"""Your One-Time Password (OTP) is: {otp}
        This code will expire in 5 minutes.
        Do not share this code with anyone. 
        Our team will never ask for your OTP.
        If you did not request this, please ignore this email."""
        ,subtype="plain")
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=503)
    