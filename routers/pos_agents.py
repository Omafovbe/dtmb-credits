from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from db import models, schemas

from db.crud import add_bulk_agent, get_agent_by_id, get_agents, get_current_user
from dependency import get_db

router = APIRouter(
    prefix='/agents',
    tags=['POS-Agents']
)

@router.get('', response_model=list[schemas.POS_AgentBase], summary='Display all Agents')
async def show_agents(db: AsyncSession = Depends(get_db), skip: int = None, limit: int = None, current_user: schemas.UserBase = Depends(get_current_user)):
    agents = await get_agents(skip=skip, limit=limit, db=db)
    return agents


@router.get('/{terminal_id}')
async def get_one_agent(terminal_id: str, db: AsyncSession = Depends(get_db)):
    resp = await get_agent_by_id(terminal_id, db=db)
   
    return resp


@router.post('', summary='Create Agent Profile', status_code=status.HTTP_201_CREATED, response_model=schemas.POS_AgentBase)
async def add_agent(db: AsyncSession = Depends(get_db)):
    return {'message': 'Create an agent profile'}


@router.post('/bulk')
async def add_multiple_agent(file: UploadFile = File(..., title='Agents File Upload', 
                                                     description='Upload a .csv file with headers as **terminal_id**, **account_number** and **agent_name** so as to add multiple agents with their account details to database'), 
                             db: AsyncSession = Depends(get_db)):
    df = await add_bulk_agent(file, db=db)
    return df