from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, WebSocket, WebSocketDisconnect, Request
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy import select
from database import get_db
from oauth2 import get_current_tenant
import models, schemas, utils, oauth2
from typing import List
from uuid import UUID
from fastapi.templating import Jinja2Templates
router = APIRouter(prefix="/ws")
r = redis.Redis(host="localhost")

@router.websocket("/deliveries/drivers/{driver_token}")
async def driver_location(websocket: WebSocket, driver_token: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.driver_token == driver_token))).scalars().first()
    if not delivery:
        await websocket.close()
        return
    try:
        while True:
            data = await websocket.receive_json()
            lat = data["lat"]
            lng = data["lng"]
            await r.set(f"{delivery.id}:lat",lat)
            await r.set(f"{delivery.id}:lng",lng)
            
    except WebSocketDisconnect:
        pass

@router.websocket("/deliveries/customers/{customer_token}")
async def driver_location(websocket: WebSocket, customer_token: str, db: AsyncSession = Depends(get_db)):

    await websocket.accept()
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.customer_token == customer_token))).scalars().first()
    if not delivery:
        await websocket.close()
        return
    try:
        while True:
            await asyncio.sleep(1)
            lat = (await r.get(f"{delivery.id}:lat")).decode()
            lng = (await r.get(f"{delivery.id}:lng")).decode()
            await websocket.send_json({"lat": float(lat), "lng": float(lng)})

    except WebSocketDisconnect:
        pass
