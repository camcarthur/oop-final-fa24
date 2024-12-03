from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime  # noqa: E501
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

# Enums


class Role(enum.Enum):
    """
    Represents user roles in the system.

    Attributes:
        user: Standard user with limited permissions.
        admin: Administrative user with elevated permissions.
    """
    user = "user"
    admin = "admin"


class TransactionType(enum.Enum):
    """
    Represents the type of a financial transaction.

    Attributes:
        deposit: Adding funds to an account.
        withdrawal: Removing funds from an account.
        transfer: Moving funds between accounts.
    """
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class TransactionStatus(enum.Enum):
    """
    Represents the status of a financial transaction.

    Attributes:
        pending: Transaction is not yet completed.
        completed: Transaction was successfully completed.
        failed: Transaction could not be completed.
    """
    pending = "pending"
    completed = "completed"
    failed = "failed"

# Models


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        user_id (int): Unique identifier for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        password_hash (str): Hashed password for the user.
        role (Role): Role of the user, either user or admin.
        accounts (list[Account]): List of accounts associated with the user.
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)

    accounts = relationship("Account", back_populates="user")


class Account(Base):
    """
    Represents a financial account.

    Attributes:
        account_id (int): Unique identifier for the account.
        user_id (int): Foreign key referencing the user who owns the account.
        account_type (str): Type of the account (e.g., savings, checking).
        balance (float): Current balance in the account.
        created_at (datetime): Timestamp when the account was created.
        user (User): The user who owns the account.
        transactions (list[Transaction]): List of transactions for the account.
    """
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    """
    Represents a financial transaction.

    Attributes:
        transaction_id (int): Unique identifier for the transaction.
        account_id (int): Foreign key referencing the account involved in the transaction.  # noqa: E501
        transaction_type (TransactionType): Type of the transaction (e.g., deposit, withdrawal).  # noqa: E501
        amount (float): Amount of money involved in the transaction.
        status (TransactionStatus): Status of the transaction (e.g., pending, completed).  # noqa: E501
        created_at (datetime): Timestamp when the transaction was created.
        notes (str): Optional notes or description of the transaction.
        account (Account): The account associated with the transaction.
    """
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
