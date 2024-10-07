import pytest
import mock
from tests_setup import client
from websockets_manager.ws_home_manager import ws_home_manager, WsMessage

def test_start_home_socket():
    """
    Test que prueba el establecimiento y almacenamiento de una conexion por medio de websockets orientada al home.
    """
    
    # Vaciamos el diccionario de conexiones (precondicion)
    ws_home_manager.active_connections = {}
    
    with client.websocket_connect("/partidas/"):
        num_of_connections = len(ws_home_manager.active_connections)
        
        # Revisamos que la conexion se haya almacenado.
        assert num_of_connections == 1, f"Fallo: Se esperaba que hubiera 1 conexión por websockets en el home, pero hay {num_of_connections}."
    
    # Revisamos que la conexion se haya eliminado.
    num_of_connections = len(ws_home_manager.active_connections)
    assert num_of_connections == 0, f"Fallo: Se esperaba que no hubieran conexiones por websockets en el home, pero hay {num_of_connections} conexiones."
    
    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_home_manager.active_connections = {}


# Este fixture evita que anyio intente usar trio, y use unicamente la libreria asyncio.
@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio()
async def test_home_manager_actualizar_partidas():
    """
    Test que prueba el funcionamiento unitario del broadcast del home_manager.
    """

    # Creamos un diccionario de falsos websockets
    fake_active_connections = {i: mock.AsyncMock() for i in range(0,10)}

    # Modificamos el diccionario de conexiones existentes
    ws_home_manager.active_connections = fake_active_connections

    # Enviamos un mensaje por broadcast
    await ws_home_manager.send_actualizar_partidas()

    # Revisamos si se llamaron todos los falsos websockets con el mensaje adecuado, una unica vez.
    for fake_connection in ws_home_manager.active_connections.items():
        connection_id, fake_ws = fake_connection

        assert fake_ws.send_text.call_count == 1, f"Fallo: Se esperaba que el websocket de id {connection_id} recibiera un único mensaje."
        
        # Revisamos que el mensaje sea el que se corresponde con la especificacion de la api.
        fake_ws.send_text.assert_called_with(
            WsMessage(action="actualizar_partidas").json()
        )
        
    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_home_manager.active_connections = {}
