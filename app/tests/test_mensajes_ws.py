import mock
from tests_setup import client
from websockets_manager.ws_home_manager import MessageType as MtHome, WsMessage as HomeMessage
from websockets_manager.ws_partidas_manager import MessageType as MtPartidas, WsMessage as PartidasMessage
from schemas import PartidaData, PartidaDetails, JugadorData
from models import Jugador
from factory import listas_to_casillas_figura

ACTUALIZAR_PARTIDAS = HomeMessage(action=MtHome.ACTUALIZAR_PARTIDAS)
# ----------------------------------------------------------
ACTUALIZAR_SALA_ESPERA = PartidasMessage(action=MtPartidas.ACTUALIZAR_SALA_ESPERA)
ACTUALIZAR_TURNO = PartidasMessage(action=MtPartidas.ACTUALIZAR_TURNO)
PARTIDA_CANCELADA = PartidasMessage(action=MtPartidas.PARTIDA_CANCELADA)
ACTUALIZAR_TABLERO = PartidasMessage(action=MtPartidas.ACTUALIZAR_TABLERO)
ACTUALIZAR_CARTAS_MOVIMIENTO = PartidasMessage(action=MtPartidas.ACTUALIZAR_CARTAS_MOVIMIENTO)
ACTUALIZAR_CARTAS_FIGURA = PartidasMessage(action=MtPartidas.ACTUALIZAR_CARTAS_FIGURA)

def test_create_partida_ws(expected_msgs_home_ws):
    with mock.patch('routers.partidas.crud.create_partida', new=mock.MagicMock()) as mock_create_partida:
        partida_data = PartidaData(nombre_partida='Partida', nombre_creador='Creador')

        mock_create_partida.return_value = PartidaDetails(
            nombre_partida=partida_data.nombre_partida,
            nombre_creador=partida_data.nombre_creador,
            id=1,
            id_creador=1,
            iniciada=False            
        )
        
        response = client.post('/partidas/', json=partida_data.model_dump())

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_home_ws.append(ACTUALIZAR_PARTIDAS)


# ----------------------------------------------------------
def test_unirse_partida_ws(expected_msgs_home_ws, expected_msgs_partidas_ws):
    with mock.patch('routers.jugadores.crud.create_jugador', new=mock.MagicMock()) as mock_create_jugador:
        jugador_data = JugadorData(
            nombre='Jugador'
        )
        
        mock_create_jugador.return_value = Jugador(id_jugador=1, nombre='Jugador', partida_id=1)
        
        response = client.post('/partidas/1/jugadores', json=jugador_data.model_dump())

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_home_ws.append(ACTUALIZAR_PARTIDAS)
    expected_msgs_partidas_ws.append(ACTUALIZAR_SALA_ESPERA)

def test_iniciar_partida_ws(expected_msgs_home_ws, expected_msgs_partidas_ws):
    with mock.patch('routers.partidas.crud.iniciar_partida', new=mock.MagicMock()) as mock_create_jugador:
        response = client.put('/partidas/1/')

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_home_ws.append(ACTUALIZAR_PARTIDAS)
    expected_msgs_partidas_ws.append(ACTUALIZAR_SALA_ESPERA)


def test_terminar_turno_ws(expected_msgs_partidas_ws):
    with mock.patch('routers.juego.crud.juego.terminar_turno', new=mock.MagicMock()) as mock_create_jugador:
        response = client.put('/juego/1/jugadores/1/turno')

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    expected_msgs_partidas_ws.append(ACTUALIZAR_TURNO)
    expected_msgs_partidas_ws.append(ACTUALIZAR_TABLERO)

# ----------------------------------------------------------

def test_abandonar_partida_sin_ganador_ws(expected_msgs_home_ws, expected_msgs_partidas_ws):
    with mock.patch('routers.partidas.crud.abandonar_partida', new=mock.MagicMock()) as mock_delete_jugador:
        mock_delete_jugador.return_value = {"hay_ganador": None, "partida_cancelada": None}
        
        response = client.delete('/partidas/1/jugadores/1')

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_home_ws.append(ACTUALIZAR_PARTIDAS)
    expected_msgs_partidas_ws.append(ACTUALIZAR_TURNO)
    expected_msgs_partidas_ws.append(ACTUALIZAR_SALA_ESPERA)
    expected_msgs_partidas_ws.append(ACTUALIZAR_TABLERO)

def test_abandonar_partida_con_ganador_ws(expected_msgs_partidas_ws):
    with mock.patch('routers.partidas.crud.abandonar_partida', new=mock.MagicMock()) as mock_delete_jugador:
        mock_delete_jugador.return_value = {"hay_ganador": {"id_ganador": 2, "nombre_ganador": "Juanito"}, "partida_cancelada": None}
        
        response = client.delete('/partidas/1/jugadores/1')

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    ganador_msg = PartidasMessage(action=MtPartidas.HAY_GANADOR, data=str({"id":2, "nombre":"Juanito"}))
    expected_msgs_partidas_ws.append(ganador_msg)

def test_abandonar_partida_ycancelar_ws(expected_msgs_home_ws, expected_msgs_partidas_ws):
    with mock.patch('routers.partidas.crud.abandonar_partida', new=mock.MagicMock()) as mock_delete_jugador:
        mock_delete_jugador.return_value = {"hay_ganador": None, "partida_cancelada": {"id": 1}}
        
        response = client.delete('/partidas/1/jugadores/1')

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_home_ws.append(ACTUALIZAR_PARTIDAS)
    expected_msgs_partidas_ws.append(PARTIDA_CANCELADA)
    
# ----------------------------------------------------------

def test_completar_figura_propia_con_ganador_ws(expected_msgs_partidas_ws):
    with mock.patch('routers.juego.crud.juego.completar_figura_propia', new=mock.MagicMock()) as mock_service:
        mock_service.return_value = {"hay_ganador": {"id_ganador": 2, "nombre_ganador": "Juanito"}}
        
        # Construimos un request body de ejemplo
        casillas_figura = listas_to_casillas_figura([[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]])[0]
        request_body = {
            "figura": casillas_figura,
            "carta_fig": "f1"
        }
        
        response = client.put('/juego/1/jugadores/2/tablero/figura', json=request_body)
        
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    ganador_msg = PartidasMessage(action=MtPartidas.HAY_GANADOR, data=str({"id":2, "nombre":"Juanito"}))
    expected_msgs_partidas_ws.append(ganador_msg)

def test_completar_figura_propia_ws(expected_msgs_partidas_ws):
    with mock.patch('routers.juego.crud.juego.completar_figura_propia', new=mock.MagicMock()) as mock_service:
        mock_service.return_value = {"hay_ganador": None}
        
        # Construimos un request body de ejemplo
        casillas_figura = listas_to_casillas_figura([[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]])[0]
        request_body = {
            "figura": casillas_figura,
            "carta_fig": "f1"
        }
        
        response = client.put('/juego/1/jugadores/2/tablero/figura', json=request_body)
        
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
    expected_msgs_partidas_ws.append(ACTUALIZAR_CARTAS_FIGURA)
    expected_msgs_partidas_ws.append(ACTUALIZAR_CARTAS_MOVIMIENTO)