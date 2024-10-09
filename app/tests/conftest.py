import pytest
from tests_setup import TestingSessionLocal, engine
from models import Base
import mock
from websockets_manager.ws_home_manager import ws_home_manager, WsMessage

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

@pytest.fixture(scope='function')
def actions_ws():
    fake_active_connections = {i: mock.AsyncMock() for i in range(0,10)}
    ws_home_manager.active_connections = fake_active_connections
    
    actions_ws = []
    
    yield actions_ws
    
    assert actions_ws != [], "FATAL ERROR: actions_ws esta vacio. (error de programacion)"
    
    for action in actions_ws:
        # Revisamos si se llamaron todos los falsos websockets con el mensaje adecuado, una unica vez.
        for fake_connection in ws_home_manager.active_connections.items():
            connection_id, fake_ws = fake_connection

            assert fake_ws.send_text.call_count == 1, f"Fallo: Se esperaba que el websocket de id {connection_id} recibiera un único mensaje."
            
            # Revisamos que el mensaje sea el que se corresponde con la especificacion de la api.
            fake_ws.send_text.assert_called_with(
                WsMessage(action=action).json()
            )
        
    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_home_manager.active_connections = {}
