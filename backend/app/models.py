from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    employee_no = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    account = relationship("Account", uselist=False, back_populates="user")

class Account(Base):
    __tablename__ = "accounts"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    current_balance = Column(Integer, default=0, nullable=False)  # 円相当のポイント
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="account")

class Charge(Base):
    __tablename__ = "charges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    payroll_withheld = Column(Integer, default=0)
    charged_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # use/charge/adjust
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

