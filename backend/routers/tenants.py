from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import select, or_
from database import get_db
from oauth2 import get_current_tenant
import models, schemas, utils, oauth2
from typing import List
from twilio.rest import Client
from config import settings
from fastapi.templating import Jinja2Templates
from config import conf
from fastapi_mail import MessageSchema, FastMail
from datetime import datetime, timezone
from typing import Optional
from tasks import driver_link_email, customer_link_email, tenant_email
from config import limiter
from fastapi import BackgroundTasks

templates = Jinja2Templates(directory="../frontend")

client = Client(settings.account_sid, settings.auth_token)
router = APIRouter(prefix="/tenants")

@router.get("/register")
@limiter.limit("10/minute")
async def driver_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_tenant(background_tasks: BackgroundTasks, data: schemas.TenantCreate, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(models.OTP).where(models.OTP.email == data.email).order_by(models.OTP.created_at.desc()).limit(5))).scalars().all()
    if not rows:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    row = None
    for r in rows:
        if utils.verify(data.otp, r.hashed_otp):
            row = r 
            break
    if not row:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.now(timezone.utc) > row.expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    try:
        password = utils.hash(data.password)
        tenant = models.Tenant(**data.model_dump(exclude={"password", "otp"}), password = password)
        db.add(tenant)
        row.is_used = True
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    background_tasks.add_task(tenant_email, data.email)
    return JSONResponse(status_code=201, content={"message": "created"})   

    
@router.post("/drivers", status_code=201)
async def create_driver(data: schemas.DriverCreate, db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    try:
        driver = models.Driver(**data.model_dump(), tenant_id = tenant.id)
        db.add(driver)
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="email")
    
@router.get("/drivers", response_model=List[schemas.DriverResponse])
async def drivers(request: Request, search: str = None, db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    query = select(models.Driver).where(models.Driver.tenant_id == tenant.id)
    print(search, "hi")
    if search:
        query = query.where(models.Driver.name.ilike(f"%{search}%"))
    
    query = query.order_by(models.Driver.created_at.desc())
    drivers = (await db.execute(query)).scalars().all()
    return drivers

@router.get("/drivers{id}", response_model=schemas.DriverResponse)
async def get_drivers(db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    driver = (await db.execute(select(models.Driver).where(models.Driver.tenant_id == tenant.id).where(models.Driver.id == id))).scalars().first()
    return driver

@router.patch("/drivers/{id}", status_code=200)
async def deactivate(id: int, data: schemas.DriverUpdate, db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    driver = (await db.execute(select(models.Driver).where(models.Driver.tenant_id == tenant.id).where(models.Driver.id == id))).scalars().first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = False if data.is_active else True
    await db.commit()
    return

@router.post("/deliveries")
async def create_delivery(background_tasks: BackgroundTasks, data: schemas.DeliveryCreate, db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    driver = (await db.execute(select(models.Driver).where(models.Driver.id == data.driver_id).where(models.Driver.tenant_id == tenant.id))).scalars().first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver does'nt exist")
    if not driver.is_active:
        raise HTTPException(status_code=403, detail="Driver is not active")
    delivery = models.Delivery(**data.model_dump(), tenant_id = tenant.id)
    db.add(delivery)
    await db.commit()
    background_tasks.add_task(driver_link_email, str(driver.email), delivery.driver_token)
    background_tasks.add_task(customer_link_email, str(data.customer_email), delivery.customer_token)
    return JSONResponse(status_code=201, content={"message": "created"})   


@router.get("/deliveries", response_model= List[schemas.DeliveryResponse])
async def get_deliveries(driver_id: Optional[int]= None, customer: str = None, status: str = None, db: AsyncSession = Depends(get_db), tenant: dict = Depends(get_current_tenant)):
    query = select(models.Delivery).where(models.Delivery.tenant_id == tenant.id)
    print(driver_id)
    if driver_id:
        query = query.where(models.Delivery.driver_id == driver_id)
    if customer:
        query = query.where(or_(models.Delivery.customer_name.ilike(f"%{customer}%"),models.Delivery.customer_email.ilike(f"%{customer}%")))
    valid_statuses = ["assigned", "en_route", "delivered", "cancelled"]
    if status and status in valid_statuses:
        query = query.where(models.Delivery.status == status)
    query = query.order_by(models.Delivery.created_at.desc())
    deliveries = (await db.execute(query)).scalars().all()
    return deliveries

