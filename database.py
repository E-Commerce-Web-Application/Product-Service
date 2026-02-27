from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'postgresql://neondb_owner:npg_sxVP0La8YzQG@ep-rapid-frog-ai7em2t5-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()