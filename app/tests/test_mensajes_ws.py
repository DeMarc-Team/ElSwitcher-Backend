import mock
from tests_setup import client
from websockets_manager.ws_home_manager import MessageType as mt_home
from websockets_manager.ws_partidas_manager import MessageType as mt_partidas
from schemas import PartidaData, PartidaDetails

ACTUALIZAR_PARTIDAS = mt_home.ACTUALIZAR_PARTIDAS.value
# ----------------------------------------------------------
ACTUALIZAR_SALA_ESPERA = mt_partidas.ACTUALIZAR_SALA_ESPERA
ACTUALIZAR_TURNO = mt_partidas.ACTUALIZAR_TURNO

def test_mensaje_actualizar_partidas(actions_ws):
    with mock.patch('routers.partidas.crud', new=mock.MagicMock()) as mock_crud:
        partida_data = PartidaData(nombre_partida='Partida', nombre_creador='Creador')

        mock_crud.create_partida.return_value = PartidaDetails(
            nombre_partida=partida_data.nombre_partida,
            nombre_creador=partida_data.nombre_creador,
            id=1,
            id_creador=1,
            iniciada=False            
        )
        
        response = client.post('/partidas/', json=partida_data.model_dump())

        assert response.status_code == 200, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
        
    actions_ws.append(ACTUALIZAR_PARTIDAS)
