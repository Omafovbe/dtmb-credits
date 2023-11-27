from fastapi import APIRouter, Depends
from decouple import config
from dependency import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from db import schemas
from db.crud import get_current_user, credit_customer


router = APIRouter(
    prefix='/payments',
    tags=['Automated Payments'],
    dependencies=[Depends(get_current_user)]
)

@router.get('')
async def get_payments():
    return {'message': 'remita payments'}


@router.post('', summary='Credit Customer from GL', 
             description=
             """**Credit a customer.** This service requires
             \n
             - retrieval reference 
             - Narration
             - Customer Account Number
             - Amount in kobo (N100.50 = 10050kobo)
             \n
             """
             )
async def credit_single_customer(
    payment: schemas.creditCustomer = Depends(), 
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    
    result = await credit_customer(db, payment, user=current_user)
    # return result.json()
    return result