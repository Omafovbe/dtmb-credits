from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Form, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from db import schemas, crud
from dependency import get_db
from decouple import config

router = APIRouter(
    prefix='/users',
    tags=['Users'],
    responses={404: {'description': 'Not found'}}
)


@router.get('', response_model= list[schemas.UserList], status_code=status.HTTP_200_OK)
async def read_users(skip: int = None, limit: int = None, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

@router.post('', 
             status_code=status.HTTP_201_CREATED, response_description='User Creation Successful',
             response_model=schemas.UserBase,
             description='Create or add a user to the database',
             dependencies=[Depends(crud.current_admin_role)]
             )
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud.create_user(db=db, user=user)
    return user


@router.get('/user', response_model=schemas.UserBase, response_description='Returns the profile of a user in the database')
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_single_user(db=db, username=username)
    return user

@router.put('/password-change')
async def update_password(
    password: Annotated[str, Form(...)], 
    confirm_password: Annotated[str, Form(...)], 
    db: AsyncSession = Depends(get_db),
    current_user: schemas.UserBase = Depends(crud.get_current_user)):
    
    if (password != confirm_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Password do not match'
        )
    
    result = await crud.update_user_password(db=db, password=password, user=current_user)
    return result


@router.post('/token', response_model=schemas.Token)
async def login_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_expires = timedelta(minutes=config('access_token_expire_min', cast=int))
    access_token = await crud.create_access_token(
        data={'sub': f'{user.username}-{user.id}', 'name': user.fullname}, 
        expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}

@router.delete('/remove', dependencies=[Depends(crud.current_admin_role)])
async def delete_user(
    username: Annotated[str, Form(...)],
    cur_user: schemas.UserBase = Depends(crud.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await crud.remove_user(db, username, cur_user)
    return result