from models import Jugador, Partida, CartaFigura

# --------------------------------Response--------------------------------
def check_response(response, status_code_esperado, respuesta_esperada):
    assert response.status_code == status_code_esperado, \
        f"Fallo: Se esperaba el estado {status_code_esperado}, pero se obtuvo {response.status_code}:{response.json()}"
    assert response.json() == respuesta_esperada, \
        f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

# --------------------------------Base de datos--------------------------------

# Test de abandonar partida
def check_jugador_abandoned(test_db, numero_de_jugadores_esperados, id_jugador_que_abandono, id_partida):
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()

    assert len(partida.jugadores) == numero_de_jugadores_esperados, \
        f"Fallo: Se esperaban {numero_de_jugadores_esperados} jugadores en la partida, pero se obtuvo {len(partida.jugadores)}"
    assert partida.jugador_del_turno.id != id_jugador_que_abandono, \
        f"Fallo: Se esperaba que el jugador del turno no fuera el jugador que abandonó, pero se obtuvo {partida.jugador_del_turno.id}"

    jugador = test_db.query(Jugador).filter(
        Jugador.id == id_jugador_que_abandono).first()
    assert jugador == None, \
        f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

def check_partida_deletion(test_db, id_partida):
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()
    assert partida == None, \
        f"Fallo: Se esperaba que la partida fuera eliminada de la base de datos, pero se encontró {partida}"

def check_cartas_figura_reveladas(jugador: Jugador, expected_codigos_figura: list[str]):
    codigos_cartas_reveladas_restantes = [carta_revelada.figura for carta_revelada in jugador.mazo_cartas_de_figura if carta_revelada.revelada]
    assert codigos_cartas_reveladas_restantes == expected_codigos_figura, \
        f"Fallo: Se esperaba que el jugador tuviera {expected_codigos_figura} cartas revelada pero tiene {codigos_cartas_reveladas_restantes}."