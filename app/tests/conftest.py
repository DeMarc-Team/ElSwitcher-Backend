import pytest
from tests_setup import TestingSessionLocal, engine
from models import Base
import mock
from unittest.mock import patch
from contextlib import ExitStack

from websockets_manager.ws_home_manager import MessageType as MThome, ws_home_manager, WsMessage as WsHomeMessage
from websockets_manager.ws_partidas_manager import MessageType as MTpartidas, ws_partidas_manager, WsMessage as WsPartidasMessage


@pytest.fixture(scope='function')
def test_ws():
    ws_home_manager_path = 'websockets_manager.ws_home_manager.ws_home_manager'
    ws_partidas_manager_path = 'websockets_manager.ws_partidas_manager.ws_partidas_manager'
    
    # Generar diccionario automáticamente
    home_ws = {message_type.value: 0 for message_type in MThome}
    partidas_ws = {message_type.value: 0 for message_type in MTpartidas}
    test_ws = {**home_ws, **partidas_ws}
    
    with ExitStack() as stack:
        mocks = {}
        for message_type in MThome:
            mocks[message_type.value] = stack.enter_context(patch(f'{ws_home_manager_path}.send_{message_type.value}'))
        for message_type in MTpartidas:
            mocks[message_type.value] = stack.enter_context(patch(f'{ws_partidas_manager_path}.send_{message_type.value}'))

        yield test_ws
        print(test_ws)

        # Realizar asserts dinámicos
        for message_type, mock in mocks.items():
            print(message_type)
            assert mock.call_count == test_ws[message_type], \
                f"Se esperaba que se llame función send_{message_type} {test_ws[message_type]} veces y se la llamo {mock.call_count}."


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
def expected_msgs_home_ws():
    # Se crean conexiones falsas
    fake_active_connections = {i: mock.AsyncMock() for i in range(0, 10)}
    ws_home_manager.active_connections = fake_active_connections

    expected_msgs_home_ws: WsHomeMessage = []

    yield expected_msgs_home_ws

    assert expected_msgs_home_ws != [
    ], "FATAL ERROR: expected_msgs_home_ws esta vacio. (error de programacion)"

    # Revisamos si se llamaron todos los falsos websockets con el mensaje adecuado, una unica vez.
    for fake_connection in ws_home_manager.active_connections.items():
        connection_id, fake_ws = fake_connection
        
        numero_mensajes = len(expected_msgs_home_ws)
        assert fake_ws.send_text.call_count == numero_mensajes, f"Fallo: Se esperaba que el websocket de id {
            connection_id} recibiera {numero_mensajes} mensajes."
        
        # Revisamos que el mensaje sea el que se corresponde con la especificacion de la api.
        fake_ws.send_text.assert_has_calls(
            [mock.call(message.json()) for message in expected_msgs_home_ws], any_order=True
        )

    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_home_manager.active_connections = {}


@pytest.fixture(scope='function')
def expected_msgs_partidas_ws():
    # Se crean conexiones falsas para una supuesta partida de id 1
    fake_active_connections = {i: mock.AsyncMock() for i in range(0, 10)}
    fake_partida_id = 1
    ws_partidas_manager.active_connections[fake_partida_id] = fake_active_connections

    expected_msgs_partidas_ws: WsPartidasMessage = []

    yield expected_msgs_partidas_ws

    assert expected_msgs_partidas_ws != [
    ], "FATAL ERROR: expected_msgs_partidas_ws esta vacio. (error de programacion)"

    # Revisamos si se llamaron todos los falsos websockets con el mensaje adecuado, una unica vez.
    for fake_connection in ws_partidas_manager.active_connections[fake_partida_id].items():
        connection_id, fake_ws = fake_connection

        numero_mensajes = len(expected_msgs_partidas_ws)
        assert fake_ws.send_text.call_count == numero_mensajes, f"Fallo: Se esperaba que el websocket de id {
            connection_id} recibiera {numero_mensajes} mensajes."

        # Revisamos que el mensaje sea el que se corresponde con la especificacion de la api.
        fake_ws.send_text.assert_has_calls(
            [mock.call(message.json()) for message in expected_msgs_partidas_ws], any_order=True
        )

    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_partidas_manager.active_connections = {}
