from random import randrange
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependency import get_db
from fastapi.encoders import jsonable_encoder
from datetime import date
from decouple import config
import requests

from db import schemas


from db.crud import credit_single_agent, current_admin_role, uploadfile1, get_current_user, get_transaction

# url2 = "https://staging.mybankone.com/thirdpartyapiservice/apiservice/CoreTransactions/Credit"


router = APIRouter(
    prefix='/transactions',
    tags=['POS-Transactions'],
    dependencies=[Depends(current_admin_role)]
)

@router.get('')
async def read_transactions(skip: int= None, limit:int = 20, db:AsyncSession = Depends(get_db)):
    trans = await get_transaction(db, skip, limit)
    return trans
    # return {'message': 'All Transactions'}


@router.post('')
async def credit_an_agent(
    transaction: schemas.transactionBase = Depends(), 
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    
    result = await credit_single_agent(db, transaction)
    return result.json()



@router.post('/upload')
async def bulk_agent_credit(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
    ):
    df = await uploadfile1(file, db=db)
    # print(df)
    # return {'message': 'Terminal_ID'}
    # return jsonable_encoder(df)
    return df

@router.post('/verify')
async def verify_payment(transQuery: schemas.transactionQuery = Depends()):
    
    headers = {
    "accept": "application/json",
    "content-type": "application/json"
    }
    
    # fmt = f'{date.today()}{randrange(9999)}'
    # payload = {
    # "RetrievalReference": "202310168877",
    # "TransactionDate": "20230112",
    # "TransactionType": None,
    # "Amount": None,
    # "Token": config('auth_token')
    # }


    
    result = requests.post(url=config('TransactionStatusQuery'), data=transQuery.model_dump_json(), headers=headers)
    # print(result.text)
    res = result.json()
    return res