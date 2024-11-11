from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "maindata.db")
URL_DATABASE = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(URL_DATABASE)

localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()
