from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

URL_DATABASE = os.getenv("DATABASE")
if not URL_DATABASE:
    raise ValueError("DATABASE environment variable not set!")

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_connection():
    return psycopg2.connect(URL_DATABASE)