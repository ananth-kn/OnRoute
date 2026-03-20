from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DATE, TIME, Enum, Boolean, UniqueConstraint, Numeric
from datetime import datetime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from typing import Annotated
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(Integer, primary_key= True)
    name = Column(String, nullable= False)
    email = Column(String, nullable= False, unique= True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone = True), server_default= text('now()'))

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

    __table_args__ = (
        UniqueConstraint("email", "tenant_id"),
    )

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_lat = Column(Numeric(7,4), nullable=True)
    customer_lng = Column(Numeric(7,4), nullable=True)
    status = Column(Enum("assigned", "en_route", "delivered", "cancelled", name="delivery_status"), nullable=False, server_default="assigned")
    driver_token = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    customer_token = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True)
    notes = Column(String, nullable=True)
    started_at = Column(TIMESTAMP(timezone=True), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class OTP(Base):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True)
    hashed_otp = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_used = Column(Boolean, server_default="false")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
