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
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/deliveries")

@router.get("/customers/{token}", response_model= schemas.DeliveryResponse)
async def get_deliveries(token: str, db: AsyncSession = Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.customer_token == token))).scalars().first()
    return delivery

@router.get("/drivers/{token}", response_model= schemas.DeliveryResponse)
async def get_deliveries(token: str, db: AsyncSession = Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.driver_token == token))).scalars().first()
    return delivery

