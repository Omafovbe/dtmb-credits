from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
from decouple import config

# from dependency import oauth2_scheme

# from db.schemas import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


