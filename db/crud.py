import codecs
import csv
from datetime import date, timedelta, datetime
from random import randint
from jose import JWTError, jwt
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from auth.security import get_hashed_password, verify_password
from fastapi import Depends, UploadFile, HTTPException, status

from decouple import config

from logs.log_config import logger
from dependency import get_db, oauth2_scheme
import pandas as pd
import requests

from db import models, schemas


def to_df(file, dest='transactions'):
    data = file.file
    data = csv.reader(codecs.iterdecode(data,'utf-8'), delimiter=',')
    header = data.__next__()
    df = pd.DataFrame(data, columns=header)
    if (dest == 'transactions'):
        df = df[['Terminal_ID','From_Account_ID','Tran_Amount_Rsp','Response_Code_description','Transaction_Status1']]
    
    return df


# Users CRUD Operations
async def get_user_id(db: AsyncSession, user_id: int):
    pass


async def get_users(db: AsyncSession, skip:int = 0, limit:int = 20):
    results = await db.execute(select(models.User).offset(skip).limit(limit))
    users = results.scalars().all()
    return  users 


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    password1 = get_hashed_password(user.password)
    db_user = models.User(
        username = user.username,
        fullname = user.fullname,
        hashed_password = password1,
        role = user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    logger.info(f'Added user-{db_user.username} to database')
    return db_user


async def update_user_password(db: AsyncSession, password: str, user):
    try:
        new_password = get_hashed_password(password)
        stmt = update(models.User).where(models.User.id == user.id).values(hashed_password=new_password)
        
        logger.info(stmt)
        await db.execute(stmt)
        await db.commit()
        
    except:
        logger.error('Error while updating user password')
        logger.exception('Database error')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Database error'
        )
    
    return {'message': 'Password updated successfully'}


async def get_single_user(db: AsyncSession, username: str):
    stmt = select(models.User).where(models.User.username == username)
    try:
        response = await db.scalars(stmt)
        user = response.one()
    except NoResultFound:
        raise HTTPException(
            status_code=400,
            detail=f'Username - {username}, does not exist'
        )
    else:  
        return schemas.UserInDb(**user.__dict__)


# Access Token definitions

async def authenticate_user(db: AsyncSession, username: str, password:str):
    user = await get_single_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, config('secret_key'), algorithm=config('algorithm'))
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail='Access Credentials could not be validated',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, config('secret_key'), algorithms=[config('algorithm')])
        username_plus: str = (payload.get('sub')).split('-')
        # logger.warn(username_plus)
        if username_plus is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(username_plus=username_plus[0])

    except JWTError:
        raise credentials_exception
    
    user = await get_single_user(db=db, username=token_data.username_plus)
    if user is None:
        raise credentials_exception
    return user

async def current_admin_role(current_user: schemas.UserBase = Depends(get_current_user)):
    print(current_user)
    if current_user.role != schemas.AdminRole.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized for this operation'
        )
    return current_user


# Transactions CRUD Operations

async def get_transaction():
    pass

async def create_transaction():
    pass

async def verify_transaction():
    pass

async def update_transaction():
    pass

async def credit_single_agent(db: AsyncSession, transaction):
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    # fmt = f'{date.today()}{randint(1001,9999)}'
    # transaction.RetrievalReference = (fmt).replace("-", "")

    transaction.Token = config('auth_token_prod')
    transaction.GLCode = config('glcode_prod')
    # (
    #    Token = '123456',
    #    GLCode = '1530' 
    # ) 

    print(transaction)
    # transaction.GLCode = '1530'
    try:
        result = requests.post(url=config('credit_uri_prod'), data=transaction.model_dump_json(), headers=headers)
    except requests.Timeout:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail='Request Timed Out.'
        )
    except requests.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='No Connection established to process your request'
        )
    else:
        # Get the agent account details

        # db_transact = models.Transactions(
        #     retrieval_ref = transaction.RetrivalReference,
        #     amount = transaction.amount,
        #     pos_id = i['pos_id'],
        #     reference = resp['Reference'],
        #     status = i['status']
        # )
        # db.add(db_transact)
        # await db.commit()
        # await db.refresh(db_transact)
        return result

async def uploadfile1(file: UploadFile, db= AsyncSession):
    df = to_df(file)
    
    records = df.to_dict(orient='records')
    returned_result = []

    if (len(records) > 100):
        logger.exception('Exceeded the total number of transactions required')
        return {'message': 'Reduce the number of transactions to 100'}
    
    for i in records:
        if i['Transaction_Status1'] == 'Not Successful':
            i.clear()
            continue
            
        if i['Transaction_Status1'] == 'Successful':
            fmt = f'{date.today()}{randint(1001,9999)}'
            retrievalNumber = (fmt).replace("-", "")
            try:
                res = await db.scalars(
                    select(models.POS_Agents)
                    .where(models.POS_Agents.terminal_id == i['Terminal_ID'])
                        )
                transact = res.one()
            except  NoResultFound:
                i.update({'status': schemas.StatusEnum.notAvailable})
            
            else:
                amount = i['Tran_Amount_Rsp']+'00'
                i.update({
                    'amount': amount,
                    'account_number': transact.account_number,
                    'status': schemas.StatusEnum.pending,
                    'pos_id': transact.id,
                    'RetrievalReference': retrievalNumber
                    })
            del i['Tran_Amount_Rsp']

            try:
                data = schemas.transactionBase = {
                    'RetrievalReference': i['RetrievalReference'],
                    'AccountNumber': i['account_number'],
                    # 'NibssCode': config('nibsscode'),
                    'Amount': i['amount'],
                    'Narration': 'POS Transaction refunds',
                    'Token': config('auth_token_stage'),
                    'GLCode': config('glcode')
                }
                print(data)
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json"
                }
                result = requests.post(url=config('credit_uri'), json=data, headers=headers)
            except requests.RequestException:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='There was an error processing your request'
                )
            else:
                logger.info(result.text)
                resp = result.json()

                if(resp['IsSuccessful']):
                    i.update({'status': schemas.StatusEnum.completed})

                    returned_result.append({**resp, **i})

                    db_transact = models.Transactions(
                        retrieval_ref = i['RetrievalReference'],
                        amount = i['amount'],
                        # amount = '1000',
                        pos_id = i['pos_id'],
                        reference = resp['Reference'],
                        status = i['status']

                    )
                    db.add(db_transact)
                    await db.commit()
                    await db.refresh(db_transact)
                else:
                    returned_result.append({**resp})


    return returned_result



# Agent CRUD operations

async def get_agents(db: AsyncSession, skip: int, limit:int):
    results = await db.execute(select(models.POS_Agents).offset(skip).limit(limit))
    agents = results.scalars().all()
    return  agents 


async def get_account():
    pass


async def get_agent_by_id(terminal_id: str, db: AsyncSession):
    # results = await db.execute(select(models.POS_Agents).offset(skip).limit(limit))
    try:
        stmt = select(models.Transactions, models.POS_Agents).join(models.POS_Agents.transactions) \
            .where(models.POS_Agents.terminal_id == terminal_id)
        
        res = await db.scalars(stmt)
        # agent, trans = res.all()
        logger.warn(stmt)
    except  NoResultFound:
        return {'error': f'No result was seen for your search on {terminal_id}'}
    # await db.commit()
    # print(type(agent))
    else:
        # print(agent., trans)
        return  res.all()


async def create_agent():
    pass

async def add_bulk_agent(file: UploadFile, db: AsyncSession):
    df = to_df(file, dest='agents')
    agent_dict = df.to_dict(orient='records')
    try:
        result = await db.scalars(insert(models.POS_Agents).returning(models.POS_Agents), agent_dict)
        ret_result = result.all()
        await db.commit()
    except (RuntimeError, TypeError, FileNotFoundError):
        return {'error': 'An error occured. Try again...'}
    else:
        return {'msg': 'Successful', 'total_data': len(ret_result)}



async def del_agent():
    pass


async def update_agent():
    pass