from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import engine, Base
from . import models, crud, schemas, auth
from .deps import get_db, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ohiru-no-pekkle - Employee Meal Points")

@app.get("/")
def root():
    return {"message": "Hello Cloud Run"}

@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect employee_no or password")
    access_token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_employee_no(db, payload.employee_no):
        raise HTTPException(status_code=400, detail="employee_no already registered")
    user = crud.create_user(db, payload)
    return user

@app.get("/me/balance", response_model=schemas.BalanceOut)
def my_balance(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    acct = crud.get_balance(db, current_user.id)
    if not acct:
        raise HTTPException(status_code=404, detail="account not found")
    return {"user_id": acct.user_id, "current_balance": acct.current_balance}

@app.post("/admin/users/create", response_model=schemas.UserOut)
def admin_create_user(payload: schemas.UserCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    if crud.get_user_by_employee_no(db, payload.employee_no):
        raise HTTPException(status_code=400, detail="employee_no already registered")
    user = crud.create_user(db, payload)
    return user

@app.get("/admin/users", response_model=list[schemas.UserListItem])
def admin_list_users(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    rows = crud.list_users_with_stats(db)
    return rows

@app.post("/admin/charge")
def admin_charge(payload: schemas.ChargeIn, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    try:
        acct = crud.charge_account(db, payload.user_id, payload.amount, payload.payroll_withheld)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user_id": acct.user_id, "current_balance": acct.current_balance}

@app.post("/use")
def use_points(payload: schemas.UseIn, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin" and current_user.id != payload.user_id:
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        acct = crud.use_points(db, payload.user_id, payload.amount, payload.operator_id, payload.description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"user_id": acct.user_id, "current_balance": acct.current_balance}

@app.get("/admin/transactions", response_model=list[schemas.TransactionOut])
def admin_transactions(current_user = Depends(get_current_user), db: Session = Depends(get_db), user_id: int | None = None):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    txs = crud.get_transactions(db, user_id=user_id)
    return txs
