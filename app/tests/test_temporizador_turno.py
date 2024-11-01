import pytest
import asyncio

from factory import crear_partida, unir_jugadores
from tools import get_all_tables, capturar_metadata as capturar, comparar_capturas, verificar_diccionarios
from verifications import check_response
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import ACTUALIZAR_SALA_ESPERA, ACTUALIZAR_TURNO, ACTUALIZAR_TABLERO
from conftest import MOCK_DURACION, MOCK_TIME_GMT

"""Lista de control, que casos de test se debe testear?
- [] Que el temporizador de turno pase el turno correctamente en 3 turnos.
- [] Que si el jugador del turno pasa turno, se cancele el temporizador y 
se inicie uno nuevo para el siguiente jugador y este pueda pasar turno.
- [] Que si el jugador del turno abandona la partida, se cancele el temporizador 
al pasar turno y se inicie uno nuevo para el siguiente jugador.
- [] Como esto no forma parte de la db, que se cancelen los temporizadores al
eliminar una partida (i.e: al haber un ganador) y que se cree otra partida con 
el mismo id, pero esto no debería pasar en una misma sesión.
"""
@pytest.mark.parametrize("numero_de_jugadores", [2])
@pytest.mark.asyncio
async def test_pasar_turno_inicial_por_temporizador(client, test_db, numero_de_jugadores, test_ws_counts):
    '''
    Test que chequea que el temporizador de turno pase el turno correctamente
    al iniciar una partida (turno1_de_inicio-->turno2)
    '''
    test_ws_counts[ACTUALIZAR_PARTIDAS] = 1
    test_ws_counts[ACTUALIZAR_SALA_ESPERA] = 1
    
    #test_ws_counts[ACTUALIZAR_TURNO] = 1
    #test_ws_counts[ACTUALIZAR_TABLERO] = 1
    
    # Inicializamos la precondición
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores-1)
    
    response = client.put("partidas/1")
    jugador_inicial = partida.jugador_del_turno
    jugador_siguiente = partida.jugadores[1]
    check_response(response, 200, {"details": "Partida iniciada correctamente", "partida_id": 1})
    
    await asyncio.sleep(MOCK_DURACION*1.6)
    test_db.refresh(partida)
    assert partida.jugador_del_turno != jugador_inicial, "El jugador debería haber pasado de turno"
    assert partida.jugador_del_turno == jugador_siguiente, "El jugador debería haber pasado de turno"

@pytest.mark.parametrize("numero_de_jugadores", [2])
@pytest.mark.asyncio
async def test_pasar_turno_segundo_por_temporizador(client, test_db, numero_de_jugadores, test_ws_counts):
    '''
    Test que chequea que el temporizador de turno pase el turno correctamente
    luego de ya haber pasado turno (turno1_de_inicio---manual-->turno2--->turno3)
    '''
    test_ws_counts[ACTUALIZAR_PARTIDAS] = 1
    test_ws_counts[ACTUALIZAR_SALA_ESPERA] = 1
    
    test_ws_counts[ACTUALIZAR_TURNO] = 1
    test_ws_counts[ACTUALIZAR_TABLERO] = 1
    
    # Inicializamos la precondición
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores-1)
    
    
    response = client.put("partidas/1")
    check_response(response, 200, {"details": "Partida iniciada correctamente", "partida_id": 1})
    jugador_inicial = partida.jugador_del_turno
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
    jugador_turno2 = partida.jugador_del_turno
    assert jugador_turno2 != jugador_inicial, "El jugador debería haber pasado de turno"
    jugador_turno3 = partida.jugadores[1]
    check_response(response, 200, None)
    
    await asyncio.sleep(MOCK_DURACION*1.6)
    test_db.refresh(partida)
    assert partida.jugador_del_turno != jugador_turno2, "El jugador debería haber pasado de turno"
    assert partida.jugador_del_turno == jugador_turno3, "El jugador debería haber pasado de turno"
