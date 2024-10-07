import pytest
import mock
from tests_setup import client
from websockets_manager.ws_partidas_manager import ws_partidas_manager, WsMessage, MessageType

def test_start_partidas_socket():
    """
    Test que prueba el establecimiento y almacenamiento de una conexion por medio de websockets orientada a cada partida en específico.
    """

    # Vaciamos el diccionario de conexiones (precondicion)
    ws_partidas_manager.active_connections = {}

    partida_id = 1
    jugador_id = 2

    with client.websocket_connect(f"/partidas/{partida_id}/jugador/{jugador_id}"):
        partidas_connections = ws_partidas_manager.active_connections
        
        # Revisamos que se haya creado un diccionario para la partida
        assert len(partidas_connections) == 1, f"Fallo: Se esperaba que hubiera 1 diccionario de partidas, pero hay {len(partidas_connections)}."

        # Revisamos que la entrada se corresponda con la de la partida de partida_id
        real_partida_key = list(partidas_connections.keys())[0]
        assert (partida_id == real_partida_key), f"Fallo, se esperaba que la entrada existente fuera la de la partida con id {partida_id}, pero es {real_partida_key}."

        # Revisamos que haya un unico websocket de jugador en la partida
        jugadores_connections = partidas_connections[partida_id]
        assert len(jugadores_connections) == 1, f"Fallo: Se esperaba que hubiera 1 websocket de un jugador en la partida de id {partida_id}, pero hay {len(jugadores_connections)}."

        # Revisamos que sea la conexion correcta
        real_jugador_key = list(jugadores_connections.keys())[0]
        assert (jugador_id == real_jugador_key), f"Fallo, se esperaba que la entrada existente fuera del jugador con id {jugador_id}, pero es {real_jugador_key}."

    # Revisamos que la conexion se haya eliminado.
    num_of_connections = len(partidas_connections)
    assert num_of_connections == 0, f"Fallo: Se esperaba que no hubieran conexiones por websockets en el home, pero hay {num_of_connections} conexiones."

    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_partidas_manager.active_connections = {}


# Este fixture evita que anyio intente usar trio, y use unicamente la libreria asyncio.
@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio()
async def test_partidas_manager_broadcast():
    """
    Test que prueba el funcionamiento principal del broadcast del partidas_manager.
    """

    # Creamos dos diccionarios de falsos websockets
    fake_active_connections = {i: mock.AsyncMock() for i in range(0,4)}
    fake_partida_id = 0

    # Modificamos el diccionario de conexiones existentes
    ws_partidas_manager.active_connections[fake_partida_id] = fake_active_connections

    # Enviamos un mensaje por broadcast a todos los "jugadores" de cada partida
    await ws_partidas_manager.broadcast(fake_partida_id, WsMessage(action=MessageType.ACTUALIZAR_SALA_ESPERA))
    
    fake_jugadores_connections = ws_partidas_manager.active_connections[fake_partida_id]
    
    # Revisamos si se llamaron todos los falsos websockets con el mensaje adecuado, una unica vez
    for fake_connection in fake_jugadores_connections.items():
        fake_jugador_id, fake_ws = fake_connection

        assert fake_ws.send_text.call_count == 1, f"Fallo: Se esperaba que el jugador de id {fake_jugador_id} recibiera un único mensaje."
        
        # Revisamos que el mensaje sea el que se corresponde con la especificacion de la api
        fake_ws.send_text.assert_called_with(
            WsMessage(action=MessageType.ACTUALIZAR_SALA_ESPERA).json()
        )
        
    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_partidas_manager.active_connections = {}
    

@pytest.mark.anyio()
async def test_partidas_mensajes_disjuntos():
    """
    Test que chequea que un broadcast se envíe solo a las conexiones de una partida y no a las del resto.
    """

    # Creamos dos diccionarios de falsos websockets
    fake_active_connections1 = {i: mock.AsyncMock() for i in range(0,4)}
    fake_active_connections2 = {i: mock.AsyncMock() for i in range(0,4)}

    # Modificamos el diccionario de conexiones existentes
    ws_partidas_manager.active_connections[1] = fake_active_connections1
    ws_partidas_manager.active_connections[2] = fake_active_connections2

    # Enviamos un mensaje por broadcast a todos los "jugadores" de la primera partida
    await ws_partidas_manager.broadcast(1, WsMessage(action=MessageType.ACTUALIZAR_SALA_ESPERA))

    # Revisamos si se llamaron todos los falsos websockets de la primera partida, una unica vez
    for fake_connection in ws_partidas_manager.active_connections[1].items():
        fake_jugador_id, fake_ws = fake_connection
        assert fake_ws.send_text.call_count == 1, f"Fallo: Se esperaba que el jugador de id {fake_jugador_id} recibiera un único mensaje."
        
    # Revisamos que no hayan llamados a los jugadores de la segunda partida
    for fake_connection in ws_partidas_manager.active_connections[2].items():
        fake_jugador_id, fake_ws = fake_connection
        assert fake_ws.send_text.call_count == 0, f"Fallo: Se esperaba que el jugador de id {fake_jugador_id} no recibiera mensajes."    
    
    # Vaciamos el diccionario de conexiones para no interferir con otros tests
    ws_partidas_manager.active_connections = {}
