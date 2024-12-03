from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime  # noqa: E501
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

# Enums


class Role(enum.Enum):
    user = "user"
    admin = "admin"


class TransactionType(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

# Models


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)

    accounts = relationship("Account", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.account_id"),
        nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    account = relationship("Account", back_populates="transactions")
