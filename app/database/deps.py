import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")


if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session