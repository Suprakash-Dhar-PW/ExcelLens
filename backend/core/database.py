import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_db_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        import logging
        logging.error(f"Database connection failed: {e}")
        return False
    finally:
        db.close()