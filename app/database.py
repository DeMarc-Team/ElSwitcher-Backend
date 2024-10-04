from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "maindata.db")
URL_DATABASE = f"sqlite:///{DATABASE_PATH}" # Definir la ruta de la base de datos

engine = create_engine(URL_DATABASE) # Crear el motor de la base de datos

localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Crear la sesión local

class Base(DeclarativeBase): # Crear la clase Base para los modelos
    pass

Base.metadata.create_all(bind=engine) # Crear las tablas basadas en la metadata de Base

def get_db(): # Función para obtener la sesión
    db = localSession()
    try:
        yield db
    finally:
        db.close()
