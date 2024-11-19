from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Account, Transaction, Role, TransactionType, TransactionStatus

# Database connection URL
DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"

# Create the database engine
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine) # create all the tables


from sqlalchemy.sql import text

# allow privilages
with engine.connect() as conn:
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO banking_user;"))
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO banking_user;"))

Session = sessionmaker(bind=engine)
session = Session()

def delete_all_data(): # deletes data for testing purposes since no dupes allowed
    """Delete all data from the database (does not drop tables)."""
    try:
        session.query(Transaction).delete()
        session.query(Account).delete()
        session.query(User).delete()

        session.commit()
        print("All data deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error occurred while deleting data: {e}")

def test_database():
    # uncomment this line if you want to clear the database before testing
    delete_all_data()

    existing_user = session.query(User).filter_by(username="test_user").first()
    if not existing_user:
        user = User(
            username="test_user",
            email="test_user@example.com",
            password_hash="hashed_password",
            role=Role.user
        )
        session.add(user)
        session.commit()

    user = session.query(User).filter_by(username="test_user").first()

    # account creation
    account = Account(
        user_id=user.user_id,
        account_type="checking",
        balance=1000.00
    )
    session.add(account)
    session.commit()

    # transaction
    transaction = Transaction(
        account_id=account.account_id,
        transaction_type=TransactionType.deposit,
        amount=500.00,
        status=TransactionStatus.completed
    )
    session.add(transaction)
    session.commit()

    print("Users:", session.query(User).all())
    print("Accounts:", session.query(Account).all())
    print("Transactions:", session.query(Transaction).all())

if __name__ == "__main__":
    test_database()
