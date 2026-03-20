from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic_settings import BaseSettings
from slowapi import Limiter
from slowapi.util import get_remote_address

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

    model_config = {
        "env_file": ".env",
        "extra": "forbid"
    }
settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.my_gmail_name,
    MAIL_PASSWORD= settings.gmail_app_password,
    MAIL_FROM= settings.my_gmail_id,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

