from sqlalchemy import (
    Column, String, ForeignKey, DateTime, Enum, Numeric, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# Enum Definitions
class Role(enum.Enum):
    user = "user"
    admin = "admin"

class TransactionType(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"

class TransactionStatus(enum.Enum):
    completed = "completed"
    failed = "failed"

# User Table
# ... [other imports and code remain the same]

# User Table
class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.user)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    accounts = relationship("Account", back_populates="user")

    __table_args__ = (
        Index('ix_username', 'username'),
        Index('ix_email', 'email')
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}', role='{self.role.value}')>"

# Account Table
class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship(
        "Transaction",
        primaryjoin="or_(Account.account_id == Transaction.account_id, Account.account_id == Transaction.target_account_id)",
        back_populates="account",
    )

    def __repr__(self):
        return f"<Account(account_id={self.account_id}, user_id={self.user_id}, account_type='{self.account_type}', balance={self.balance})>"

# Transaction Table
class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.account_id'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(TransactionStatus), nullable=False)
    target_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.account_id'), nullable=True)

    account = relationship(
        "Account",
        foreign_keys=[account_id],
        back_populates="transactions",
        overlaps="transactions, target_account",
    )
    target_account = relationship(
        "Account",
        foreign_keys=[target_account_id],
        overlaps="transactions, account",
    )

    __table_args__ = (
        Index('ix_account_id_timestamp', 'account_id', 'timestamp'),
    )

    def __repr__(self):
        return (f"<Transaction(transaction_id={self.transaction_id}, account_id={self.account_id}, "
                f"transaction_type='{self.transaction_type.value}', amount={self.amount}, "
                f"timestamp={self.timestamp}, status='{self.status.value}', "
                f"target_account_id={self.target_account_id})>")
