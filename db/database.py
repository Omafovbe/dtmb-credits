from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///./dtmb-pos.db'

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

