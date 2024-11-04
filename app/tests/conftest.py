from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from collections import Counter
from unittest.mock import patch
import time
import pytest
import os

import sys # Estas dos lineas modifican las importanciones de los modulos en los tests
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from database import Base, get_db
from main import app
from tools import WSManagerTester; tester = WSManagerTester()
from factory import test_temporizadores_turno, MOCK_GMT_TIME_ZT

# Setup de la base de datos de prueba
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Configurar logging para que muestre solo los errores
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING) # Si se quiere ver los queries, cambiar a INFO

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope='session')
def client():
    # Sobreescribir la dependencia de base de datos
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)

@pytest.fixture(scope='function')
def test_db():
    # Limpiamos la base de datos antes de cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Creamos una nueva sesión de base de datos para cada test
    db = TestingSessionLocal()
    with patch('crud.repository.BaseRepository.session', db): # Para que repository use la misma session que el test
        yield db
    db.close()

@pytest.fixture(scope='function', autouse=True)
def mock_dict_temporizadores_turno():
    # Mockeamos el diccionario del temporizador de turno
    with patch("crud.TemporizadorTurno.temporizadores_turno", test_temporizadores_turno):
        yield
        test_temporizadores_turno.limpiar_temporizadores()

@pytest.fixture(scope='function')
def mock_timeGmt():
    time_struct_to_mock = time.struct_time([2024, 11, 3, 15, 30, 0, 7, 2, 3])
    with patch("time.gmtime", return_value=time_struct_to_mock):
        yield MOCK_GMT_TIME_ZT
        
@pytest.fixture(autouse=True, scope='session')
def teardown_db():
    yield
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'test.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"El archivo de base de datos {db_path} ha sido eliminado.")
        else:
            print(f"El archivo de base de datos {db_path} no existe.")
    except Exception as e:
        print(f"Error al eliminar el archivo de base de datos: {e}")

@pytest.fixture(scope='function')
def test_ws_counts():
    def assert_mock_counts(test_ws, mocks):
        # Realizar asserts dinámicos
        for message_type, mock in mocks.items():
            print(message_type)
            assert mock.call_count == test_ws[message_type], \
                    f"Se esperaba que se llame función send_{message_type} {test_ws[message_type]} veces y se la llamo {mock.call_count}."
    
    yield from tester.test_ws_factory(0, assert_mock_counts)

@pytest.fixture(scope='function')
def test_ws_messages():
    # Función de aserción para comparar las llamadas reales con los mensajes esperados
    def assert_message_calls(test_ws, mocks):
        for message_type, mock in mocks.items():
            # Obtener los llamados actuales en forma de diccionarios
            actual_calls = tester.inspect_mock_calls(mock)
            expected_messages = test_ws[message_type]
            
            print(f"Llamadas actuales para '{message_type}': {actual_calls}")
            
            # Usamos Counter para comparar las listas de diccionarios sin importar el orden
            assert Counter(map(lambda x : str(x), actual_calls)) == Counter(map(lambda x : str(x), expected_messages)), \
                f"send_{message_type} recibió: {actual_calls} pero esperaba {expected_messages}."

    yield from tester.test_ws_factory([], assert_message_calls)
