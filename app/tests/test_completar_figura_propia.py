import pdb
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida, establecer_tablero, cartear_figuras, listas_to_casillas_figura
from verifications import check_response
from schemas import Casilla

def test_usar_figura_propia(test_db):
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)
    jugador_del_turno = partida.jugador_del_turno

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

    establecer_tablero(test_db, partida, tablero_mock)
    cartear_figuras(test_db, jugador_del_turno, ["f1"])

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }

    # Solicitamos el uso de la figura
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Chequeamos que se haya consumido la carta correctamente
    cartas_reveladas_restantes = [carta_revelada for carta_revelada in jugador_del_turno.mazo_cartas_de_figura if carta_revelada.revelada]
    assert cartas_reveladas_restantes == [], f"Fallo: Se esperaba que el jugador agotara su única carta, pero le quedan {len(cartas_reveladas_restantes)}."
