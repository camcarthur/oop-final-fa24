import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from database.models import Base, User, Account, Transaction
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"

@pytest.fixture(scope="module")
def engine():
    """Provide a connection to the existing database."""
    return create_engine(DATABASE_URL)

@pytest.fixture(scope="module")
def session(engine):
    """Provide a session for interacting with the database."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_tables_exist(engine):
    """Test that all tables are created."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = {"users", "accounts", "transactions"}
    assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"

def test_insert_user(session):
    """Test inserting a user record."""
    new_user = User(username="testuser", email="test@example.com", password_hash="hashed_password", role="user")
    session.add(new_user)
    session.commit()

    queried_user = session.query(User).filter_by(username="testuser").first()
    assert queried_user is not None
    assert queried_user.email == "test@example.com"

    # Clean up
    session.delete(queried_user)
    session.commit()
