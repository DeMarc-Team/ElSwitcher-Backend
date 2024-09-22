import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db

# Configuramos la Base de Datos de pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creamos de la Base de Datos de pruebas,
# con todas las tablas definidas en el modelo de datos (definido en app.database).
Base.metadata.create_all(bind=engine)

# Sobreescribimos de la Dependencia de la Base de Datos get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db

# Creamos del cliente de pruebas
client = TestClient(app)