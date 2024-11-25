import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DEV_DATABASE_URL = os.getenv("DEV_DATABASE_URL")
engine = create_engine(DEV_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()


def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
