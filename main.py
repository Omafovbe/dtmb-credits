from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logs.log_config import logger
from routers import pos_agents, users, transactions
from dependency import APIProcessTime, LogMiddleWare

app = FastAPI(
    title='Delta Trust POS Transaction API',
    version= '0.1.0',
    summary= 'To manage transactions, users and agents with terminal IDs',
    description= 'An API to automate and carryout transactions on POS with terminal IDs linked to their Delta Trust Accounts'
)


origins = [
    'http://localhost:8000',
    'http://localhost:3000'
]

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins
)
app.add_middleware(APIProcessTime)
app.add_middleware(LogMiddleWare)

# Routes
app.include_router(users.router)
app.include_router(pos_agents.router)
app.include_router(transactions.router)


@app.get('/', tags=['Main'])
async def root():
    logger.info('Lets Begin')
    return {'message': 'Delta Trust POS Transaction API-Integration'}