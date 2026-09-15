from sqlalchemy.orm import Session
from . import models
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_employee_no(db: Session, employee_no: str):
    return db.query(models.User).filter(models.User.employee_no == employee_no).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, payload):
    hashed = pwd_context.hash(payload.password)
    user = models.User(
        employee_no=payload.employee_no,
        name=payload.name,
        email=payload.email,
        password_hash=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    account = models.Account(user_id=user.id, current_balance=0)
    db.add(account)
    db.commit()
    return user

def charge_account(db: Session, user_id: int, amount: int, payroll_withheld: int = 0):
    acct = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not acct:
        raise ValueError("account not found")
    acct.current_balance += amount
    charge = models.Charge(user_id=user_id, amount=amount, payroll_withheld=payroll_withheld, charged_at=datetime.utcnow())
    db.add(charge)
    db.add(models.Transaction(user_id=user_id, amount=amount, type="charge", description="monthly charge"))
    db.commit()
    return acct

def use_points(db: Session, user_id: int, amount: int, operator_id: int = None):
    acct = db.query(models.Account).filter(models.Account.user_id == user_id).with_for_update().first()
    if not acct:
        raise ValueError("account not found")
    if acct.current_balance < amount:
        raise ValueError("insufficient balance")
    acct.current_balance -= amount
    tx = models.Transaction(user_id=user_id, amount=amount, type="use", description=f"used by operator {operator_id}")
    db.add(tx)
    db.commit()
    return acct

