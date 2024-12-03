import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DATABASE_URL = "postgresql://banking_user:secure_password@localhost:5432/banking_db"  # noqa: E501

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
