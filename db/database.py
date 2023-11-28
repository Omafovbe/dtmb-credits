from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from decouple import config

SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./dtmb-pos.db'
SQLALCHEMY_DATABASE_URL2 = config('neon_db')
SQLALCHEMY_DATABASE_URL3 = config('postgres_database')

engine = create_async_engine(
    # SQLALCHEMY_DATABASE_URL2, connect_args={'check_same_thread': False}
    SQLALCHEMY_DATABASE_URL2
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

