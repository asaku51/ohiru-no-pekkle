from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    employee_no: str
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    employee_no: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime
    class Config:
        orm_mode = True

class ChargeIn(BaseModel):
    user_id: int
    amount: int
    payroll_withheld: Optional[int] = 0

class UseIn(BaseModel):
    user_id: int
    amount: int
    operator_id: Optional[int] = None

class BalanceOut(BaseModel):
    user_id: int
    current_balance: int
    class Config:
        orm_mode = True

