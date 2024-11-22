from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User, Account, Transaction

# Database connection URL
DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"

# Create the database engine
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)  # Create all the tables

from sqlalchemy.sql import text

# Allow privileges
with engine.connect() as conn:
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO banking_user;"))
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO banking_user;"))

Session = sessionmaker(bind=engine)
session = Session()

def delete_all_data():
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
