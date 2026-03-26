from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic_settings import BaseSettings
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis.asyncio as redis

limiter = Limiter(key_func=get_remote_address)
class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    sqlalchemy_database_url: str
    account_sid: str
    auth_token: str
    gmail_app_password: str
    my_gmail_id: str
    my_gmail_name: str
    redis_url:str
    brevo_api_key:str
    local: bool
    model_config = {
        "env_file": ".env",
        "extra": "forbid"
    }
settings = Settings()

r = redis.from_url(settings.redis_url, decode_responses=True)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.my_gmail_name,
    MAIL_PASSWORD=settings.gmail_app_password,
    MAIL_FROM=settings.my_gmail_id,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True
)

