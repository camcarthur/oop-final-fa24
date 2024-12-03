import unittest
# from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import (
    Base, User, Account, Transaction, Role,
    TransactionType, TransactionStatus
)

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"


class TestModels(unittest.TestCase):
    """Test suite for models in the database."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database and session for testing."""
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down the database after all tests."""
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self) -> None:
        """Start a new session for each test."""
        self.session = self.Session()

    def tearDown(self) -> None:
        """Rollback the session to ensure a clean state."""
        self.session.rollback()
        self.session.close()

    def test_user_creation(self) -> None:
        """Test creating a user."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            role=Role.user
        )
        self.session.add(user)
        self.session.commit()

        queried_user = self.session.query(User).filter_by(username="testuser").first()  # noqa: E501
        self.assertIsNotNone(queried_user)
        self.assertEqual(queried_user.email, "test@example.com")
        self.assertEqual(queried_user.role, Role.user)

    def test_account_creation(self) -> None:
        """Test creating an account and linking it to a user."""
        user = User(
            username="accountuser",
            email="account@example.com",
            password_hash="hashed",
            role=Role.user
        )
        self.session.add(user)
        self.session.commit()

        account = Account(
            user_id=user.user_id,
            account_type="savings",
            balance=1000.00
        )
        self.session.add(account)
        self.session.commit()

        queried_account = self.session.query(Account).filter_by(user_id=user.user_id).first()  # noqa: E501
        self.assertIsNotNone(queried_account)
        self.assertEqual(queried_account.account_type, "savings")
        self.assertEqual(queried_account.balance, 1000.00)

        # Verify relationship
        self.assertEqual(queried_account.user.username, "accountuser")

    def test_transaction_creation(self) -> None:
        """Test creating a transaction and linking it to an account."""
        user = User(
            username="transactionuser",
            email="transaction@example.com",
            password_hash="hashed",
            role=Role.user
        )
        self.session.add(user)
        self.session.commit()

        account = Account(
            user_id=user.user_id,
            account_type="checking",
            balance=500.00
        )
        self.session.add(account)
        self.session.commit()

        transaction = Transaction(
            account_id=account.account_id,
            transaction_type=TransactionType.deposit,
            amount=250.00,
            status=TransactionStatus.completed,
            notes="Initial deposit"
        )
        self.session.add(transaction)
        self.session.commit()

        queried_transaction = self.session.query(Transaction).filter_by(
            account_id=account.account_id
        ).first()
        self.assertIsNotNone(queried_transaction)
        self.assertEqual(queried_transaction.transaction_type, TransactionType.deposit)  # noqa: E501
        self.assertEqual(queried_transaction.amount, 250.00)
        self.assertEqual(queried_transaction.status, TransactionStatus.completed)  # noqa: E501
        self.assertEqual(queried_transaction.notes, "Initial deposit")

        # Verify relationship
        self.assertEqual(queried_transaction.account.account_type, "checking")


if __name__ == "__main__":
    unittest.main()
