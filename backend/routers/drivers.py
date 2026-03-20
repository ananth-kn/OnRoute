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
templates = Jinja2Templates(directory="../frontend")

router = APIRouter(prefix="/drivers")



@router.get("/map/{driver_token}")
async def driver_page(request: Request, driver_token: str):
    return templates.TemplateResponse("driver.html", {"request": request, "driver_token": driver_token})

