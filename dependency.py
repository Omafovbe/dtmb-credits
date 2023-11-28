import time
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from db.database import SessionLocal, engine, Base

from logs.log_config import logger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/token')


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


class APIProcessTime(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers['X-Process-Time'] = str(process_time)
        return response


class LogMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logger.info(
            msg=f'{request.method} {request.url} {response.status_code}')
        return response
