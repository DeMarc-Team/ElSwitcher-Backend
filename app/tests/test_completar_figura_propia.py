import pdb
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida, establecer_tablero, cartear_figuras
from verifications import check_response
from schemas import Casilla

def test_usar_figura_propia(test_db):
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)
    
    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]
    
    resaltadas_en_el_mock = {
        "figuras_a_resaltar": {
            "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]],
            "f2": [],
            "f3": [],
            "f4": [],
        }
    }
    
    establecer_tablero(test_db, partida, tablero_mock)
    cartear_figuras(test_db, creador, ["f1"])
    
    casillas_figura = []
    for casilla in resaltadas_en_el_mock["figuras_a_resaltar"]["f1"][0]:
        casillas_figura.append({
            "row": casilla[0],
            "col": casilla[1]
        }
        )
    
    
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    
    response = client.put(f'/juego/{partida.id}/jugadores/{creador.id_jugador}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)