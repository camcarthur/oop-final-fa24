from sqlalchemy.orm import Session
from database.models import User, Account, Transaction, TransactionType, TransactionStatus



class BaseFactory:
    def __init__(self, session: Session):
        self.session = session

    def create(self, **kwargs):
        raise NotImplementedError("Subclasses must implement the 'create' method.")


class UserFactory(BaseFactory):
    def create(self, username: str, email: str, password_hash: str, role="user"):
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        self.session.add(user)
        self.session.commit()
        return user


class AccountFactory(BaseFactory):
    def create(self, user_id, account_type, balance=0.00):
        account = Account(
            user_id=user_id,
            account_type=account_type,
            balance=balance
        )
        self.session.add(account)
        self.session.commit()
        return account


class TransactionFactory(BaseFactory):
    def create(self, account_id, transaction_type, amount, status):
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            status=status
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction

