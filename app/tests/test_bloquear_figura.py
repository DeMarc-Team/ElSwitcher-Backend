import pytest

from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import ACTUALIZAR_SALA_ESPERA, ACTUALIZAR_TURNO, HAY_GANADOR, PARTIDA_CANCELADA, ACTUALIZAR_TABLERO
from factory import (
    crear_partida,
    unir_jugadores,
    iniciar_partida,
    establecer_tablero,
    cartear_figuras,
    listas_to_casillas_figura,
    falsear_movimientos_parciales,
)
from verifications import check_response

def test_bloquear_happy_path(client, test_db):
    # Tablero que deseamos que se utilice
    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]

    # Diccionario con las casillas de las figuras formadas en el tablero del mock
    figuras_formadas_en_mock = {
        "figuras_a_resaltar": {
            "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]]
        }
    }

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "id_jugador_bloqueado": 2,
        "figura": casillas_figura,
        "carta_fig": "f1"
    }

    # Configuramos el escenario
    partida, jugador_del_turno, jugador_a_bloquear = configurar_test_bloqueos(test_db, tablero_mock, mano_del_jugador_a_bloquear=["f1"], n_movimientos_a_consumir=1)
    
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/bloquear-carta', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

def configurar_test_bloqueos(test_db, tablero_mock, mano_del_jugador_a_bloquear, n_movimientos_a_consumir):
    '''
    Configura un escenario medianamente general para los tests de completar figuras.
    
    A la salida de este procedimiento, la base de datos test_db queda con:
    - Una nueva partida iniciada
    - El jugador del turno tendrá en su mazo las cartas reveladas con los códigos de "cartas_figura_carteadas"
    - "n_movimientos_a_consumir" del jugador determina cuántas cartas de movimiento del jugador del turno estarán "parcialmente usadas"
    
    Retorna: 
    partida, jugador_del_turno
    '''
    
    
    # Creamos las bases de la partida
    partida, _ = crear_partida(test_db)
    jugador_a_bloquear = unir_jugadores(test_db, partida, numero_de_jugadores=1)[0]
    iniciar_partida(test_db, partida)
    
    # Configuramos particularidades del jugador que posee el turno
    establecer_tablero(test_db, partida, tablero_mock)
    
    jugador_del_turno = partida.jugador_del_turno   # Por construcción del factory, tiene que ser el creador
    
    cartear_figuras(test_db, jugador_a_bloquear, mano_del_jugador_a_bloquear)
    
    movimientos_a_consumir = jugador_del_turno.mano_movimientos[0:n_movimientos_a_consumir]
    falsear_movimientos_parciales(test_db, partida, movimientos_a_consumir)

    return partida, jugador_del_turno, jugador_a_bloquear
