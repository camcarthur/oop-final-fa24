from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Database connection URL
DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"

# Create the database engine
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)  # Create all the tables

# Define the session factory
Session = sessionmaker(bind=engine)
session = Session()
