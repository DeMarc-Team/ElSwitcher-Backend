from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

URL_DATABASE = f'sqlite:///maindata.db'

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
