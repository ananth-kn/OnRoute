from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

import ssl

if settings.local:
    engine = create_async_engine(settings.sqlalchemy_database_url)
else:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    engine = create_async_engine(
        settings.sqlalchemy_database_url,
        connect_args={"ssl": ssl_context},
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
    )
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except:
            await db.rollback()
            raise