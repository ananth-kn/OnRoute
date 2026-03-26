from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
import models, schemas
from config import limiter
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/customers")
templates = Jinja2Templates(directory="../frontend")

@router.get("/{customer_token}")
async def set_customer_location(request: Request, customer_token: str, db: AsyncSession= Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.customer_token == customer_token))).scalars().first()
    if not delivery:
            return {"message": "Page not found"}
    return templates.TemplateResponse("customer.html", {"request":request, "customer_token": customer_token})


@router.patch("/location/{customer_token}")
@limiter.limit("10/minute")
async def add_customer_location(request: Request, data: schemas.CustomerLocation, customer_token: str, db: AsyncSession= Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.customer_token == customer_token))).scalars().first()
    delivery.customer_lat = data.lat
    delivery.customer_lng = data.lng
    await db.commit()
    print("done")
    return {"message": "location updated"}

