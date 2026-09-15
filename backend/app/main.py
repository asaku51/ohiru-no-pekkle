from fastapi import FastAPI, Depends, HTTPException
from .database import engine, Base
from . import models, crud, schemas
from .deps import get_db, get_current_user
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Meal Points")

@app.get("/")
def root():
    return {"message": "Hello Cloud Run"}

@app.post("/auth/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_employee_no(db, payload.employee_no):
        raise HTTPException(status_code=400, detail="employee_no already registered")
    user = crud.create_user(db, payload)
    return user

@app.get("/me/balance", response_model=schemas.BalanceOut)
def my_balance(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    acct = db.query(models.Account).filter(models.Account.user_id == current_user.id).first()
    if not acct:
        raise HTTPException(status_code=404, detail="account not found")
    return acct

@app.post("/admin/charge")
def admin_charge(payload: schemas.ChargeIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    try:
        acct = crud.charge_account(db, payload.user_id, payload.amount, payload.payroll_withheld)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user_id": acct.user_id, "current_balance": acct.current_balance}
