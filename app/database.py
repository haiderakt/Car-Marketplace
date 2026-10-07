from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass