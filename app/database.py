import os
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
	raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
	pass

SessionLocal = sessionmaker(
	bind=engine,
	autoflush=False,
	autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

