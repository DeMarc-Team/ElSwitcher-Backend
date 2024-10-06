from tests_setup import client
from websockets_manager.ws_home_manager import ws_home_manager

def test_start_home_socket():
    """
    Test que prueba el establecimiento y almacenamiento de una conexion por medio de websockets orientada al home.
    """
    
    with client.websocket_connect("/partidas/") as websocket:
        num_of_connections = len(ws_home_manager.active_connections)
        
        # Revisamos que la conexion se haya almacenado.
        assert num_of_connections == 1, f"Fallo: Se esperaba que hubiera 1 conexión por websockets en el home, pero hay {num_of_connections}."
    
    # Revisamos que la conexion se haya eliminado.
    num_of_connections = len(ws_home_manager.active_connections)
    assert num_of_connections == 0, f"Fallo: Se esperaba que no hubieran conexiones por websockets en el home, pero hay {num_of_connections} conexiones."