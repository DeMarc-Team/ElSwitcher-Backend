import pytest
from tests_setup import TestingSessionLocal, engine
from models import Base
from collections import Counter
from tools import WSManagerTester; tester = WSManagerTester()

@pytest.fixture(scope='function')
def test_ws(): # TODO: cambiar nombre a test_ws_counts
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
            assert Counter(map(frozenset, actual_calls)) == Counter(map(frozenset, expected_messages)), \
                f"send_{message_type} recibió: {actual_calls} pero esperaba {expected_messages}."

    yield from tester.test_ws_factory([], assert_message_calls)

@pytest.fixture(scope='function')
def test_db():
    # Limpiamos la base de datos antes de cada test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Creamos una nueva sesión de base de datos para cada test
    db = TestingSessionLocal()
    yield db
    db.close()

# Eliminamos la base de datos de prueba después de todos los tests


@pytest.fixture(autouse=True, scope='session')
def teardown_db():
    yield

    import os
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'test.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"El archivo de base de datos {db_path} ha sido eliminado.")
        else:
            print(f"El archivo de base de datos {db_path} no existe.")
    except Exception as e:
        print(f"Error al eliminar el archivo de base de datos: {e}")
