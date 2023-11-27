import inspect
from typing import Annotated, Literal
from fastapi import Form
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, date
from random import randint
from decouple import config

fmt = f'{date.today()}{randint(1001,9999)}'
retrievalRef = (fmt).replace("-", "")

class AdminRole(str, Enum):
    staff = 1
    admin = 2
    acct = 3
    pos = 4

class StatusEnum(str, Enum):
    failed = 'Failed'
    pending = 'Pending'
    completed = 'Completed'
    notAvailable = 'Not Available'

class BankCode(str, Enum):
    zenith = '1011'
    uba = '1012'
    gtbank = '1013'
    fidelity = '1014'


def as_form(cls):
    new_params = [
        inspect.Parameter(
            field_name,
            inspect.Parameter.POSITIONAL_ONLY,
            default=model_field.default,
            annotation=Annotated[model_field.annotation, *model_field.metadata, Form()],
        )
        for field_name, model_field in cls.model_fields.items()
    ]

    cls.__signature__ = cls.__signature__.replace(parameters=new_params)

    return cls

class UserBase(BaseModel):
    username: str
    fullname: str
    role: AdminRole

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "some_username",
                    "fullname": "Firstname Lastname",
                    "password": "unpredictablePassword",
                    "role": "use either of 1,2,3 or 4 where 1-staff, 2-admin, 3-accounts, 4-pos"
                }
            ]
        }
    }

class UserList(UserBase):
    id: int
    created_at: datetime

class UserCreate(UserBase):
    password: str

class UserInDb(UserBase):
    id: int
    hashed_password: str

class Transactions(BaseModel):
    retrivalReference: str
    terminal_id: str
    amount: float
    status: StatusEnum
    reference: str
    created_at: datetime

class POS_AgentCreate(BaseModel):
    agent_name: str
    account_number: str
    terminal_id: str

class POS_AgentBase(POS_AgentCreate):
    id: int

class POS_AgentTrans(POS_AgentBase):
    transactions: list[Transactions]  = []

@as_form
class transactionQuery(BaseModel):
    RetrievalReference: str
    TransactionDate: str
    TransactionType: str | None = None
    Amount: str | None = None
    Token: str


@as_form
class transactionBase(BaseModel):
    RetrievalReference: str = retrievalRef
    AccountNumber: str
    NibssCode: str = config('nibsscode_prod')
    Amount: str 
    Narration: str
    Token: str | None = None
    GLCode: str | None = None
    # GLCode: Literal['Zenith', 'UBA', 'GTBank']


@as_form
class creditCustomer(BaseModel):
    RetrievalReference: str = retrievalRef
    AccountNumber: str
    NibssCode: str = config('nibsscode_prod')
    Amount: str
    Narration: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username_plus: str | None = None

