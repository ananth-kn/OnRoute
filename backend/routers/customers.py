from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, WebSocket, WebSocketDisconnect, Request
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import select
from database import get_db
from oauth2 import get_current_tenant
import models, schemas, utils, oauth2
from typing import List
from uuid import UUID
from config import limiter, r
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/customers")
templates = Jinja2Templates(directory="../frontend")

@router.get("/{customer_token}", status_code=200)
async def set_customer_location(request: Request, customer_token: str):
    return templates.TemplateResponse("customer.html", {"request":request, "customer_token": customer_token})


@router.patch("/location/{customer_token}", status_code=200)
@limiter.limit("10/minute")
async def add_customer_location(request: Request, data: schemas.CustomerLocation, customer_token: str, db: AsyncSession= Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.customer_token == customer_token))).scalars().first()
    delivery.customer_lat = data.lat
    delivery.customer_lng = data.lng
    await db.commit()
    return templates.TemplateResponse("customer.html", {"request":request, "customer_token": customer_token})


