from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from fastapi import File, UploadFile, Form
from typing import Optional, Literal
from datetime import date, time, datetime
from uuid import UUID
from decimal import Decimal

class Email(BaseModel):
    email: EmailStr

class TokenData(BaseModel):
    tenant_id: int

class TenantCreate(BaseModel):
    name: str
    password: str
    email:str
    otp: str

class DriverCreate(BaseModel):
    name: str
    email: EmailStr

class DriverResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class DeliveryCreate(BaseModel):
    driver_id: int
    customer_name: str
    customer_email: EmailStr
    notes: str | None = None

class DeliveryResponse(BaseModel):
    id: int
    driver_id: int
    customer_name: str
    customer_email: EmailStr
    status: str
    driver_token: UUID
    customer_token: UUID
    notes: str | None
    customer_lat: float | None
    customer_lng: float | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

class CustomerLocation(BaseModel):
    lat: Decimal = Field(ge=-90, le=90)
    lng: Decimal = Field(ge=-180, le=180)

class DeliveryStatus(BaseModel):
    status: Literal["assigned", "en_route", "delivered", "cancelled"]

class DriverUpdate(BaseModel):
    is_active: bool