from pydantic import BaseModel
from datetime import datetime
from typing import List

class TransactionBase(BaseModel):
    type: str
    amount: float

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    owner_name: str
    initial_balance: float = 0.0

class Account(BaseModel):
    id: int
    owner_name: str
    balance: float
    class Config:
        from_attributes = True

class UpdateBalance(BaseModel):
    amount: float