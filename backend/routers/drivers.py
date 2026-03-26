from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from fastapi.templating import Jinja2Templates
import models
templates = Jinja2Templates(directory="../frontend")

router = APIRouter(prefix="/drivers")



@router.get("/map/{driver_token}")
async def driver_page(request: Request, driver_token: str, db: AsyncSession = Depends(get_db)):
    delivery = (await db.execute(select(models.Delivery).where(models.Delivery.driver_token == driver_token))).scalars().first()
    if not delivery:
        return {"message": "Page not found"}
    return templates.TemplateResponse("driver.html", {"request": request, "driver_token": driver_token})

