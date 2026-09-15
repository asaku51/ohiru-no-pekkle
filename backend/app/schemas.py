from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    employee_no: str
    name: str
    password: str
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    id: int
    employee_no: str
    name: str
    email: Optional[EmailStr] = None
    role: str
    created_at: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChargeIn(BaseModel):
    user_id: int
    amount: int
    payroll_withheld: Optional[int] = 0

class UseIn(BaseModel):
    user_id: int
    amount: int
    operator_id: Optional[int] = None
    description: Optional[str] = None

class BalanceOut(BaseModel):
    user_id: int
    current_balance: int
    class Config:
        orm_mode = True

class UserListItem(BaseModel):
    id: int
    employee_no: str
    name: str
    monthly_used: int
    current_balance: int
    class Config:
        orm_mode = True

class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: int
    type: str
    description: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True
