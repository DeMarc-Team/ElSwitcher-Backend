import pytest

from factory import (
    crear_partida,
    unir_jugadores,
    iniciar_partida,
    establecer_tablero,
    cartear_figuras,
    listas_to_casillas_figura,
    falsear_movimientos_parciales,
)
from tools import capturar_metadata, comparar_capturas, get_all_tables
from verifications import check_response
from websockets_manager.ws_partidas_manager import ACTUALIZAR_CARTAS_MOVIMIENTO, ACTUALIZAR_CARTAS_FIGURA

def test_bloquear_happy_path(client, test_db, test_ws_messages):
    
    # Especificamos los mensajes de ws que se deberían enviar para el correcto funcionamiento
    test_ws_messages[ACTUALIZAR_CARTAS_FIGURA] = [{"partida_id": 1}]
    test_ws_messages[ACTUALIZAR_CARTAS_MOVIMIENTO] = [{"partida_id": 1}]
    
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

    # Configuramos el escenario
    partida, jugador_del_turno, jugador_a_bloquear = configurar_test_bloqueos(test_db, tablero_mock, mano_del_jugador_a_bloquear=["f1"], n_movimientos_a_consumir=2)

    # Capturamos la BDD antes de los cambios
    captura_inicial = capturar_metadata(get_all_tables(test_db))

    # Efectuamos la request
    request_body = {
        "id_jugador_bloqueado": jugador_a_bloquear.id,
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/bloquear-carta', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Capturamos la BDD luego de los cambios
    captura_final = capturar_metadata(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # 51 es, por construcción, el id de la carta carteada.
    assert set(modificaciones) == set({('cartas_de_figura', 51): [('bloqueada', False, True)]}), "Fallo: Se esperaba que hubieran otras modificaciones."
    assert set(eliminadas) == set(
        [
            ("movimientos_parciales", 1),
            ("movimientos_parciales", 2),
            ("cartas_de_movimiento", 1),
            ("cartas_de_movimiento", 2),
        ]
    ), "Fallo: Se esperaba que se eliminara otro conjunto de elementos."
    assert set(creadas) == set(), "Fallo: Se esperaba que no hubieran creaciones."

def test_bloquear_figura_inexistente_404(client, test_db, test_ws_messages):
    
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

    # Configuramos el escenario
    partida, jugador_del_turno, jugador_a_bloquear = configurar_test_bloqueos(test_db, tablero_mock, mano_del_jugador_a_bloquear=["f1", "f3"], n_movimientos_a_consumir=1)

    # Capturamos la BDD antes de los cambios
    captura_inicial = capturar_metadata(get_all_tables(test_db))

    # Efectuamos la request
    request_body = {
        "id_jugador_bloqueado": jugador_a_bloquear.id,
        "figura": casillas_figura,
        "carta_fig": "f3"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/bloquear-carta', json=request_body)
    check_response(response, status_code_esperado=404, respuesta_esperada={'detail': 'No existe (en el tablero) ninguna figura del tipo que se intenta utilizar.'})

    # Capturamos la BDD luego de los cambios
    captura_final = capturar_metadata(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # 51 es, por construcción, el id de la carta carteada.
    assert set(modificaciones) == set(), "Fallo: Se esperaba que no hubieran modificaciones."
    assert set(eliminadas) == set(), "Fallo: Se esperaba que no se eliminaran elementos."
    assert set(creadas) == set(), "Fallo: Se esperaba que no hubieran creaciones."

def configurar_test_bloqueos(test_db, tablero_mock, mano_del_jugador_a_bloquear, n_movimientos_a_consumir=0):
    '''
    Configura un escenario medianamente general para los tests de completar figuras.
    
    A la salida de este procedimiento, la base de datos test_db queda con:
    - Una nueva partida iniciada
    - El jugador_a_bloquear tendrá en su mazo las cartas reveladas con los códigos de "cartas_figura_carteadas"
    - "n_movimientos_a_consumir" determina cuántas cartas de movimiento del jugador del turno estarán "parcialmente usadas"
    
    Retorna: 
    partida, jugador_del_turno, jugador_a_bloquear
    '''
    
    # Creamos las bases de la partida
    partida, _ = crear_partida(test_db)
    jugador_a_bloquear = unir_jugadores(test_db, partida, numero_de_jugadores=1)[0]
    iniciar_partida(test_db, partida)
    
    # Configuramos particularidades del jugador que posee el turno
    establecer_tablero(test_db, partida, tablero_mock)
    
    jugador_del_turno = partida.jugador_del_turno   # Por construcción del factory, tiene que ser el creador
    
    cartear_figuras(test_db, jugador_a_bloquear, mano_del_jugador_a_bloquear)
    
    if (n_movimientos_a_consumir != 0):
        movimientos_a_consumir = jugador_del_turno.mano_movimientos[0:n_movimientos_a_consumir]
        falsear_movimientos_parciales(test_db, partida, movimientos_a_consumir)

    return partida, jugador_del_turno, jugador_a_bloquear
