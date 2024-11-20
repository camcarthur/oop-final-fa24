from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the base class for declarative models
Base = declarative_base()

# Database connection URL
DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables defined by Base subclasses
Base.metadata.create_all(engine)

# Allow privileges for testing (note: these are for local development only)
from sqlalchemy.sql import text
with engine.connect() as conn:
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO banking_user;"))
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO banking_user;"))

# Set up the database session
Session = sessionmaker(bind=engine)
db_session = Session()

# Function to delete all data for testing purposes
def delete_all_data():
    """Delete all data from the database (does not drop tables)."""
    try:
        db_session.query(Transaction).delete()
        db_session.query(Account).delete()
        db_session.query(User).delete()
        db_db_session.commit()
        print("All data deleted successfully.")
    except Exception as e:
        db_db_session.rollback()
        print(f"Error occurred while deleting data: {e}")

# Function to test the database
def test_database():
    # Uncomment this line if you want to clear the database before testing
    delete_all_data()

    existing_user = db_session.query(User).filter_by(username="test_user").first()
    if not existing_user:
        user = User(
            username="test_user",
            email="test_user@example.com",
            password_hash="hashed_password",
            role="user"
        )
        db_db_session.add(user)
        session.commit()

    user = session.query(User).filter_by(username="test_user").first()

    # Account creation
    account = Account(
        user_id=user.user_id,
        account_type="checking",
        balance=1000.00
    )
    session.add(account)
    session.commit()

    # Transaction
    transaction = Transaction(
        account_id=account.account_id,
        transaction_type="deposit",
        amount=500.00,
        status="completed"
    )
    session.add(transaction)
    session.commit()

    print("Users:", session.query(User).all())
    print("Accounts:", session.query(Account).all())
    print("Transactions:", session.query(Transaction).all())

if __name__ == "__main__":
    test_database()