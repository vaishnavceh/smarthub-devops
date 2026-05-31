from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Connect to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:smarthubtest@postgres:5432/smarthub")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Used to inject database session into API endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()