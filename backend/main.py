from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import RedirectResponse
from database import engine
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from fastapi.templating import Jinja2Templates
from oauth2 import get_current_tenant
# from routers import user, auth, doctor, slot, appointment, patient
# import models
from routers import tenants, auth, drivers, customers, deliveries, ws
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from config import settings
from database import get_db, AsyncSessionLocal
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import models, schemas, oauth2
from contextlib import asynccontextmanager
import asyncio
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
from config import limiter
templates = Jinja2Templates(directory="../frontend")

@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(run_every_5_min())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from pathlib import Path
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent / "frontend" / "static"),
    name="static"
)




async def run_every_5_min():
    while True:
        await delete_expired_otps()
        await asyncio.sleep(300)

@app.get("/", response_class=HTMLResponse)
def root():
    if 1:
        return RedirectResponse(url="/tenants/register")


conf = ConnectionConfig(
    MAIL_USERNAME=settings.my_gmail_id,
    MAIL_PASSWORD= settings.gmail_app_password,
    MAIL_FROM= settings.my_gmail_id,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)
async def delete_expired_otps():
    db = AsyncSessionLocal()
    while True:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
            await db.execute(delete(models.OTP).where(models.OTP.expires_at < cutoff))
            await db.commit()
        finally:
            await db.close()

app.include_router(tenants.router)
app.include_router(auth.router) 
app.include_router(drivers.router)
app.include_router(customers.router)
app.include_router(deliveries.router)
app.include_router(ws.router)

@app.get("/dashboard")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        tenant = await get_current_tenant(request, db)
    except HTTPException:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return RedirectResponse("/auth/login")
        try:
            try:
                payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            except JWTError:
                return RedirectResponse(url="/auth/login")
            tenant_id = payload.get("tenant_id")
            if not tenant_id:
                return RedirectResponse(url="/auth/login")
            tenant = (await db.execute(select(models.Tenant).where(models.Tenant.id == tenant_id))).scalars().first()
            if not tenant:
                return RedirectResponse(url="/auth/login")
            access_token = oauth2.create_access_token({"tenant_id":tenant.id})
            response = templates.TemplateResponse("dashboard.html", {"request": request})
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                samesite="lax",
                secure=False
            )
            print("new")
            return response
        except Exception:
            return RedirectResponse(url="/auth/login")
    return templates.TemplateResponse("dashboard.html", {"request": request})

