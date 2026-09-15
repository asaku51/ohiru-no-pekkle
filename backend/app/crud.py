from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from passlib.context import CryptContext
from datetime import datetime, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MONTHLY_LIMIT = 15000  # 月間利用上限

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

def authenticate_user(db: Session, employee_no: str, password: str):
    user = get_user_by_employee_no(db, employee_no)
    if not user:
        return None
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user

def charge_account(db: Session, user_id: int, amount: int, payroll_withheld: int = 0, note: str = None):
    acct = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    if not acct:
        raise ValueError("account not found")
    acct.current_balance += amount
    charge = models.Charge(user_id=user_id, amount=amount, payroll_withheld=payroll_withheld, charged_at=datetime.utcnow(), note=note)
    tx = models.Transaction(user_id=user_id, amount=amount, type="charge", description=note)
    db.add(charge)
    db.add(tx)
    db.commit()
    db.refresh(acct)
    return acct

def get_balance(db: Session, user_id: int):
    acct = db.query(models.Account).filter(models.Account.user_id == user_id).first()
    return acct

def use_points(db: Session, user_id: int, amount: int, operator_id: int = None, description: str = None):
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    used_sum = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == "use",
        models.Transaction.created_at >= first_of_month
    ).scalar() or 0
    if used_sum + amount > MONTHLY_LIMIT:
        raise ValueError(f"monthly limit exceeded: used {used_sum}, trying {amount}, limit {MONTHLY_LIMIT}")
    acct = db.query(models.Account).filter(models.Account.user_id == user_id).with_for_update().first()
    if not acct:
        raise ValueError("account not found")
    if acct.current_balance < amount:
        raise ValueError("insufficient balance")
    acct.current_balance -= amount
    tx = models.Transaction(user_id=user_id, amount=amount, type="use", description=description or f"used by operator {operator_id}")
    db.add(tx)
    db.commit()
    db.refresh(acct)
    return acct

def list_users_with_stats(db: Session):
    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    users = db.query(models.User).all()
    out = []
    for u in users:
        used = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
            models.Transaction.user_id == u.id,
            models.Transaction.type == "use",
            models.Transaction.created_at >= first_of_month
        ).scalar() or 0
        balance = 0
        if u.account:
            balance = u.account.current_balance
        out.append({
            "id": u.id,
            "employee_no": u.employee_no,
            "name": u.name,
            "monthly_used": int(used),
            "current_balance": int(balance)
        })
    return out

def get_transactions(db: Session, user_id: int = None, limit: int = 100):
    q = db.query(models.Transaction).order_by(models.Transaction.created_at.desc())
    if user_id:
        q = q.filter(models.Transaction.user_id == user_id)
    return q.limit(limit).all()
